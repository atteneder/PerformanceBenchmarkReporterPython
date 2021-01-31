from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List
from pathlib import Path


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
            if r.Name == name:
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
    group_name,
    all_stats=False
):

    # reference report
    ref = reports[0]

    with open(output_path, 'w') as output_file:

        output_file.write('Test Name')

        for name in report_names:
            output_file.write(f';{name}')
            if all_stats:
                output_file.write(
                    f';{name}_Min;{name}_Max;{name}_Median;{name}_Average')

        output_file.write('\n')

        for ref_result in ref.Results:
            results = [report.get_result_by_name(
                ref_result.Name) for report in reports]

            test_name = '.'.join(ref_result.Name.split('.')[3:])
            output_file.write(test_name)

            for ref_grp in ref_result.SampleGroups:
                if ref_grp.Name == group_name:
                    grps = [result.get_sample_group_by_name(
                        ref_grp.Name) for result in results]
                    for grp in grps:
                        if all_stats:
                            output_file.write(
                                f';;{grp.Min};{grp.Max};{grp.Median};{grp.Average}')
                        else:
                            output_file.write(f';{grp.Average}')
            output_file.write('\n')


def main():
    report_paths = [
        '/Users/aa/Library/Application Support/Andreas Atteneder/glTFastDemo/2.5.1/PerformanceTestResults.json',
        '/Users/aa/Library/Application Support/Andreas Atteneder/glTFastDemo/async3_json/PerformanceTestResults.json',
        # '/Users/aa/Library/Application Support/Andreas Atteneder/glTFastDemo/async4_base64/PerformanceTestResults.json',
        # '/Users/aa/Library/Application Support/Andreas Atteneder/glTFastDemo/async5_non_readable/PerformanceTestResults.json',
        '/Users/aa/Library/Application Support/Andreas Atteneder/glTFastDemo/async6_testfix/PerformanceTestResults.json',
        '/Users/aa/Library/Application Support/Andreas Atteneder/glTFastDemo/async7_dracojobs/PerformanceTestResults.json',
    ]
    report_paths = [Path(x) for x in report_paths]
    report_names = [x.parent.name for x in report_paths]
    reports = [load_report(report_path) for report_path in report_paths]

    create_load_time_report(
        '/Users/aa/u/PerformanceBenchmarkReporterPython/result.csv', report_names, reports, 'LoadTime')
    create_load_time_report('/Users/aa/u/PerformanceBenchmarkReporterPython/result_frame_time.csv',
                            report_names, reports, 'FrameTime', all_stats=True)


if __name__ == '__main__':
    main()
