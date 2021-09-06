from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List
from pathlib import Path


def remove_test_prefix(name: str):
    result = name
    result = result.removeprefix('GLTFast.Tests.')
    result = result.removeprefix('GLTFTest.')
    return result


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
            ref_name = remove_test_prefix(r.Name)
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
                    f';{name}_Min;{name}_Max;{name}_Median;{name}_Average')
            else:
                output_file.write(f';{name}')

        output_file.write('\n')

        for ref_result in ref.Results:
            ref_result_name = remove_test_prefix(ref_result.Name)
            results = [report.get_result_by_name(ref_result_name
                                                 ) for report in reports]

            if not remove_test_prefix(ref_result.Name).startswith(test_prefix):
                continue

            test_name = ref_result.Name[len(test_prefix):].lstrip('.')
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
                            output_row += f';{grp.Min};{grp.Max};{grp.Median};{grp.Average}'
                        else:
                            output_row += f';{grp.Average}'

            if output_row:
                output_file.write(output_row)
                output_file.write('\n')


def main():
    report_paths = [
        # 'input_data/mac_intel/2.6.0/PerformanceTestResults.json',
        # 'input_data/mac_intel/async3_json/PerformanceTestResults.json',
        # 'input_data/mac_intel/async4_base64/PerformanceTestResults.json',
        # 'input_data/mac_intel/async5_non_readable/PerformanceTestResults.json',
        # 'input_data/mac_intel/async6_testfix/PerformanceTestResults.json',
        # 'input_data/mac_intel/3.0.0/PerformanceTestResults.json',
        # 'input_data/mac_intel/3.0.0-1/PerformanceTestResults.json',
        # 'input_data/mac_intel/3.0.2/PerformanceTestResults.json',
        # 'input_data/mac_intel/3.1.0/PerformanceTestResults.json',
        # 'input_data/mac_intel/4.2.0/PerformanceTestResults.json',
        'input_data/mac_intel/4.2.1/PerformanceTestResults.json',
        'input_data/mac_intel/4.3.0_burst/PerformanceTestResults.json',

        # 'input_data/mac_m1/2.6.0_rosetta/PerformanceTestResults.json',
        # 'input_data/mac_m1/2.6.0/PerformanceTestResults.json',
        # 'input_data/mac_m1/3.0.0/PerformanceTestResults.json',

        # 'input_data/win/2.6.0/PerformanceTestResults.json',
        # 'input_data/win/3.0.0/PerformanceTestResults.json',
    ]
    report_paths = [Path(x) for x in report_paths]
    report_names = [x.parent.name for x in report_paths]
    reports = [load_report(report_path) for report_path in report_paths]

    create_load_time_report(
        'output/smooth_load_times.csv',
        report_names,
        reports,
        'SampleModelsTest.SmoothLoading',
        'LoadTime'
    )

    create_load_time_report(
        'output/smooth_frame_times.csv',
        report_names,
        reports,
        'SampleModelsTest.SmoothLoading',
        'Time',
        all_stats=True
    )

    create_load_time_report(
        'output/fast_load_times.csv',
        report_names,
        reports,
        'SampleModelsTest.UninterruptedLoading',
        'LoadTime'
    )


if __name__ == '__main__':
    main()
