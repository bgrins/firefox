#!/bin/bash

# Script to run intermittent tests with --headless
# and consolidate results into a report

# Configuration
TEST_FILE="intermittent_tests.txt"
REPORT_FILE="intermittent_test_report.txt"
MAX_TESTS=5  # Start with just 5 tests for initial testing
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Initialize report
echo "Intermittent Test Verification Report" > "$REPORT_FILE"
echo "Generated: $(date)" >> "$REPORT_FILE"
echo "=================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Read the first MAX_TESTS tests from the file
echo "Reading first $MAX_TESTS tests from $TEST_FILE..."
TESTS=()
while IFS= read -r line; do
    TESTS+=("$line")
done < <(head -n "$MAX_TESTS" "$TEST_FILE")

# Process each test
for TEST_NAME in "${TESTS[@]}"; do
    # Skip empty lines
    if [[ -z "$TEST_NAME" ]]; then
        continue
    fi
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo ""
    echo "[$TOTAL_TESTS/$MAX_TESTS] Running: $TEST_NAME"
    echo "Test $TOTAL_TESTS: $TEST_NAME" >> "$REPORT_FILE"
    echo "----------------------------------------" >> "$REPORT_FILE"
    
    # Run the test and capture output
    START_TIME=$(date +%s)
    ./mach test "$TEST_NAME" > "test_output_${TOTAL_TESTS}.log" 2>&1
    EXIT_CODE=$?
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    # Check result and update counters
    if [[ $EXIT_CODE -eq 0 ]]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        STATUS="PASSED"
        echo "  ✓ PASSED (${DURATION}s)"
        echo "Status: PASSED" >> "$REPORT_FILE"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        STATUS="FAILED"
        echo "  ✗ FAILED (${DURATION}s, exit code: $EXIT_CODE)"
        echo "Status: FAILED (exit code: $EXIT_CODE)" >> "$REPORT_FILE"
        
        # Extract key error messages from log
        echo "Error summary:" >> "$REPORT_FILE"
        grep -E "(ERROR|FAIL|Exception|Traceback)" "test_output_${TOTAL_TESTS}.log" | head -10 >> "$REPORT_FILE" 2>/dev/null || echo "  No specific errors captured" >> "$REPORT_FILE"
    fi
    
    echo "Duration: ${DURATION} seconds" >> "$REPORT_FILE"
    echo "Full log: test_output_${TOTAL_TESTS}.log" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
done

# Summary
echo ""
echo "================================="
echo "SUMMARY"
echo "================================="
echo "Total tests run: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"
echo ""

# Add summary to report
echo "=================================" >> "$REPORT_FILE"
echo "SUMMARY" >> "$REPORT_FILE"
echo "=================================" >> "$REPORT_FILE"
echo "Total tests run: $TOTAL_TESTS" >> "$REPORT_FILE"
echo "Passed: $PASSED_TESTS" >> "$REPORT_FILE"
echo "Failed: $FAILED_TESTS" >> "$REPORT_FILE"
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=1; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)
    echo "Success rate: ${SUCCESS_RATE}%" >> "$REPORT_FILE"
else
    echo "Success rate: N/A (no tests run)" >> "$REPORT_FILE"
fi

echo "Report saved to: $REPORT_FILE"
echo "Individual test logs saved as: test_output_*.log"