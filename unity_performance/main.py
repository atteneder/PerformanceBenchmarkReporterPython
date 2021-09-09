import argparse

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List
from pathlib import Path


CSV_SEP = ','

TEST_PREFIXES = [
    'GLTFast.Tests.',
    'GLTFTest.',
]


def remove_test_prefix(name: str):
    result = name
    for prefix in TEST_PREFIXES:
        if result.startswith(prefix):
            return prefix, result[len(prefix):]
    return None, result


@dataclass_json
@dataclass
class SampleGroup:

    Name: str

    Min: float
    Max: float
    Median: float
    Average: float
    StandardDeviation: float
    Sum: float


@dataclass_json
@dataclass
class Result:
    # Test name
    Name: str
    SampleGroups: List[SampleGroup]

    def get_sample_group_by_name(self, name):
        for r in self.SampleGroups:
            if r.Name == name:
                return r
        return None


@dataclass_json
@dataclass
class Report:
    Results: List[Result]

    def get_result_by_name(self, name):
        for r in self.Results:
            _, ref_name = remove_test_prefix(r.Name)
            if ref_name == name:
                return r
        return None


def load_report(filepath):
    with open(filepath, 'r') as report_file:
        report_json = report_file.read()

    return Report.from_json(report_json)


def create_load_time_report(
    output_path,
    report_names,
    reports,
    test_prefix,
    group_name,
    all_stats=False
):

    # reference report
    ref = reports[0]

    with open(output_path, 'w') as output_file:

        output_file.write('Test Name')

        for name in report_names:
            if all_stats:
                output_file.write(
                    f'{CSV_SEP}{name}_Min{CSV_SEP}{name}_Max{CSV_SEP}{name}_Median{CSV_SEP}{name}_Average')
            else:
                output_file.write(f'{CSV_SEP}{name}')

        output_file.write('\n')

        for ref_result in ref.Results:
            prefix, ref_result_name = remove_test_prefix(ref_result.Name)
            results = [report.get_result_by_name(ref_result_name
                                                 ) for report in reports]

            if not ref_result_name.startswith(test_prefix):
                continue

            test_name = ref_result.Name[len(prefix)+len(test_prefix):].lstrip('.')
            output_row = test_name

            for ref_grp in ref_result.SampleGroups:
                if ref_grp.Name == group_name:

                    if None in results:
                        output_row = None
                        continue

                    grps = [result.get_sample_group_by_name(
                        ref_grp.Name) for result in results]

                    if None in grps:
                        output_row = None
                        continue

                    for grp in grps:
                        if all_stats:
                            output_row += f'{CSV_SEP}{grp.Min}{CSV_SEP}{grp.Max}{CSV_SEP}{grp.Median}{CSV_SEP}{grp.Average}'
                        else:
                            output_row += f'{CSV_SEP}{grp.Average}'

            if output_row:
                output_file.write(output_row)
                output_file.write('\n')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--prefix',
        type=str,
    )

    parser.add_argument(
        '--sample-group',
        type=str,
        default='Time',
        dest='sample_group',
    )

    parser.add_argument(
        '--output',
        type=str,
    )

    parser.add_argument(
        '--all-stats',
        action='store_true',
        dest='all_stats',
    )

    parser.add_argument(
        'paths',
        type=str,
        nargs='+',
    )

    args = parser.parse_args()

    report_paths = [Path(x) for x in args.paths]
    report_names = [x.parent.name for x in report_paths]
    reports = [load_report(report_path) for report_path in report_paths]
    out_path = Path(args.output)

    create_load_time_report(
        out_path,
        report_names,
        reports,
        args.prefix,
        args.sample_group,
        args.all_stats
    )


if __name__ == '__main__':
    main()
