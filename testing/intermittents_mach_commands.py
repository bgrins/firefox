# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import logging
import os
import subprocess
import sys
import time

from intermittent_failures import IntermittentFailuresFetcher
from mach.decorators import Command, CommandArgument, SubCommand


@Command(
    "intermittents",
    category="testing",
    description="Analyze intermittent test failures",
)
def intermittents(command_context):
    """
    Utility to analyze intermittent test failures in Firefox.
    """
    # Print help text when no subcommand is provided
    print("usage: mach intermittents <subcommand> [options]")
    print()
    print("Analyze intermittent test failures in Firefox.")
    print()
    print("subcommands:")
    print("  list    List the most frequent intermittent test failures")
    print("  test    Run intermittent tests from a file")
    print()
    print("Run 'mach intermittents <subcommand> --help' for more information.")
    sys.exit(0)


@SubCommand(
    "intermittents",
    "list",
    description="List the most frequent intermittent test failures",
)
@CommandArgument(
    "--days",
    type=int,
    default=7,
    help="Number of days to look back for failures (default: 7)",
)
@CommandArgument(
    "--threshold",
    type=int,
    default=30,
    help="Minimum number of failures to include (default: 30)",
)
@CommandArgument(
    "--branch",
    default="trunk",
    help="Branch to query (default: trunk)",
)
@CommandArgument(
    "--json",
    action="store_true",
    dest="json_output",
    help="Output results as JSON",
)
@CommandArgument(
    "--verbose",
    action="store_true",
    help="Show additional details for each failure",
)
@CommandArgument(
    "--all",
    action="store_true",
    help="Show all bugs (by default only single tracking bugs with test paths are shown)",
)
def list_intermittents(
    command_context,
    days=7,
    threshold=30,
    branch="trunk",
    json_output=False,
    verbose=False,
    all=False,
):
    """List the most frequent intermittent test failures"""

    # Logging setup
    if not json_output:
        command_context.log(
            logging.INFO,
            "intermittents",
            {},
            f"Fetching intermittent failures from the last {days} days with at least {threshold} occurrences...",
        )

    fetcher = IntermittentFailuresFetcher(
        days=days, threshold=threshold, verbose=verbose and not json_output
    )

    try:
        results = fetcher.get_failures(branch=branch)
    except Exception as e:
        command_context.log(
            logging.ERROR,
            "intermittents",
            {"error": str(e)},
            "Error fetching failures: {error}",
        )
        return 1

    if not all:
        results = [
            result
            for result in results
            if result.get("test_path") and "single tracking bug" in result["summary"]
        ]

    if not results:
        if not json_output:
            message = f"No bugs found with at least {threshold} failures in the last {days} days."
            if not all:
                message = f"No single tracking bugs with test paths found with at least {threshold} failures in the last {days} days. Use --all to see all bugs."
            command_context.log(
                logging.INFO,
                "intermittents",
                {},
                message,
            )
        else:
            print(json.dumps([]))
        return 0

    results.sort(key=lambda x: x["failure_count"], reverse=True)

    if json_output:
        print(json.dumps(results, indent=2))
    else:
        command_context.log(
            logging.INFO,
            "intermittents",
            {"count": len(results), "threshold": threshold},
            "Found {count} bugs with at least {threshold} failures:",
        )
        print()

        for i, result in enumerate(results, 1):
            print(f"{i}. Bug {result['bug_id']}: {result['failure_count']} failures")
            if result.get("test_path"):
                print(f"   Test: {result['test_path']}")
            print(f"   Summary: {result['summary']}")
            print(f"   Status: {result['status']}", end="")
            if result.get("resolution"):
                print(f" - {result['resolution']}")
            else:
                print()
            if result.get("creation_time"):
                created = result["creation_time"].split("T")[0]  # Just the date part
                print(f"   Created: {created}")
            if result.get("last_change_time"):
                updated = result["last_change_time"].split("T")[0]  # Just the date part
                print(f"   Last updated: {updated}")
            if result.get("comment_count") is not None:
                print(f"   Comments: {result['comment_count']}")
            print(
                f"   URL: https://bugzilla.mozilla.org/show_bug.cgi?id={result['bug_id']}"
            )
            print()

    return 0


@SubCommand(
    "intermittents",
    "test",
    description="Run intermittent tests from a file",
)
@CommandArgument(
    "--test-file",
    default="intermittent_tests.txt",
    help="File containing test names to run (default: intermittent_tests.txt)",
)
@CommandArgument(
    "--report-file",
    default="intermittent_test_report.txt",
    help="Output file for test results (default: intermittent_test_report.txt)",
)
@CommandArgument(
    "--max-tests",
    type=int,
    default=5,
    help="Maximum number of tests to run (default: 5)",
)
@CommandArgument(
    "--timeout",
    type=int,
    default=300,
    help="Timeout per test in seconds (default: 300)",
)
def test_intermittents(
    command_context,
    test_file="intermittent_tests.txt",
    report_file="intermittent_test_report.txt",
    max_tests=5,
    timeout=300,
):
    """Run intermittent tests from a file and generate a report"""
    
    if not os.path.exists(test_file):
        command_context.log(
            logging.ERROR,
            "intermittents",
            {"file": test_file},
            "Test file not found: {file}",
        )
        return 1
    
    # Read test names from file
    tests = []
    try:
        with open(test_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    tests.append(line)
                    if len(tests) >= max_tests:
                        break
    except Exception as e:
        command_context.log(
            logging.ERROR,
            "intermittents",
            {"error": str(e)},
            "Error reading test file: {error}",
        )
        return 1
    
    if not tests:
        command_context.log(
            logging.ERROR,
            "intermittents",
            {},
            "No tests found in test file",
        )
        return 1
    
    # Initialize report
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(report_file, 'w') as f:
            f.write("Intermittent Test Verification Report\n")
            f.write(f"Generated: {timestamp}\n")
            f.write("=================================\n\n")
    except Exception as e:
        command_context.log(
            logging.ERROR,
            "intermittents",
            {"error": str(e)},
            "Error creating report file: {error}",
        )
        return 1
    
    # Counters
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    command_context.log(
        logging.INFO,
        "intermittents",
        {"count": len(tests), "file": test_file},
        "Running {count} tests from {file}...",
    )
    
    # Process each test
    for i, test_name in enumerate(tests, 1):
        total_tests += 1
        
        command_context.log(
            logging.INFO,
            "intermittents",
            {"current": i, "total": len(tests), "test": test_name},
            "[{current}/{total}] Running: {test}",
        )
        
        # Run the test
        start_time = time.time()
        log_file = f"test_output_{i}.log"
        
        try:
            result = subprocess.run(
                ["./mach", "test", test_name],
                stdout=open(log_file, 'w'),
                stderr=subprocess.STDOUT,
                timeout=timeout,
                cwd=command_context.topsrcdir,
            )
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            exit_code = 124  # Standard timeout exit code
            command_context.log(
                logging.WARNING,
                "intermittents",
                {"test": test_name, "timeout": timeout},
                "Test {test} timed out after {timeout} seconds",
            )
        except Exception as e:
            exit_code = 1
            command_context.log(
                logging.ERROR,
                "intermittents",
                {"test": test_name, "error": str(e)},
                "Error running test {test}: {error}",
            )
        
        end_time = time.time()
        duration = int(end_time - start_time)
        
        # Update counters and report
        if exit_code == 0:
            passed_tests += 1
            status = "PASSED"
            command_context.log(
                logging.INFO,
                "intermittents",
                {"duration": duration},
                "  ✓ PASSED ({duration}s)",
            )
        else:
            failed_tests += 1
            status = "FAILED"
            command_context.log(
                logging.INFO,
                "intermittents",
                {"duration": duration, "exit_code": exit_code},
                "  ✗ FAILED ({duration}s, exit code: {exit_code})",
            )
        
        # Write to report
        try:
            with open(report_file, 'a') as f:
                f.write(f"Test {i}: {test_name}\n")
                f.write("----------------------------------------\n")
                f.write(f"Status: {status}")
                if exit_code != 0:
                    f.write(f" (exit code: {exit_code})")
                f.write("\n")
                f.write(f"Duration: {duration} seconds\n")
                f.write(f"Full log: {log_file}\n")
                
                # Add error summary for failed tests
                if exit_code != 0:
                    f.write("Error summary:\n")
                    try:
                        with open(log_file, 'r') as log:
                            error_lines = []
                            for line in log:
                                if any(keyword in line.upper() for keyword in ['ERROR', 'FAIL', 'EXCEPTION', 'TRACEBACK']):
                                    error_lines.append(line.strip())
                                    if len(error_lines) >= 10:
                                        break
                            if error_lines:
                                for error_line in error_lines:
                                    f.write(f"  {error_line}\n")
                            else:
                                f.write("  No specific errors captured\n")
                    except:
                        f.write("  Could not read error details\n")
                
                f.write("\n")
        except Exception as e:
            command_context.log(
                logging.ERROR,
                "intermittents",
                {"error": str(e)},
                "Error writing to report: {error}",
            )
    
    # Summary
    command_context.log(
        logging.INFO,
        "intermittents",
        {},
        "=================================",
    )
    command_context.log(
        logging.INFO,
        "intermittents",
        {},
        "SUMMARY",
    )
    command_context.log(
        logging.INFO,
        "intermittents",
        {},
        "=================================",
    )
    command_context.log(
        logging.INFO,
        "intermittents",
        {"total": total_tests, "passed": passed_tests, "failed": failed_tests},
        "Total tests run: {total}",
    )
    command_context.log(
        logging.INFO,
        "intermittents",
        {"passed": passed_tests},
        "Passed: {passed}",
    )
    command_context.log(
        logging.INFO,
        "intermittents",
        {"failed": failed_tests},
        "Failed: {failed}",
    )
    
    # Add summary to report
    try:
        with open(report_file, 'a') as f:
            f.write("=================================\n")
            f.write("SUMMARY\n")
            f.write("=================================\n")
            f.write(f"Total tests run: {total_tests}\n")
            f.write(f"Passed: {passed_tests}\n")
            f.write(f"Failed: {failed_tests}\n")
            if total_tests > 0:
                success_rate = (passed_tests * 100) / total_tests
                f.write(f"Success rate: {success_rate:.1f}%\n")
            else:
                f.write("Success rate: N/A (no tests run)\n")
    except Exception as e:
        command_context.log(
            logging.ERROR,
            "intermittents",
            {"error": str(e)},
            "Error writing summary to report: {error}",
        )
    
    command_context.log(
        logging.INFO,
        "intermittents",
        {"report": report_file},
        "Report saved to: {report}",
    )
    
    return 0 if failed_tests == 0 else 1
