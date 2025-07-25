#!/bin/bash

# Script to run intermittent tests with --verify
# and consolidate results into a report

# Configuration
TEST_FILE="intermittent_tests.txt"
REPORT_FILE="intermittent_test_report.txt"
MAX_TESTS=3  # Start with just 3 tests for initial testing
TEST_TIMEOUT=300  # 5 minutes per test
HEADLESS=false  # Set to false to run with GUI
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
TIMEOUT_TESTS=0

# Function to run a test with timeout
run_test_with_timeout() {
    local test_name="$1"
    local log_file="$2"
    local timeout_seconds="$3"
    
    # Generate a random marionette port to avoid conflicts
    local marionette_port=$((2828 + RANDOM % 1000))
    
    # Build test command with optional headless flag
    local test_cmd="MOZ_MARIONETTE_PORT=$marionette_port ./mach test \"$test_name\" --verify"
    if [ "$HEADLESS" = true ]; then
        test_cmd="$test_cmd --headless"
    fi
    
    # Run test in background
    eval "$test_cmd > \"$log_file\" 2>&1 &"
    local pid=$!
    
    # Wait for test or timeout
    local count=0
    while kill -0 $pid 2>/dev/null; do
        if [ $count -ge $timeout_seconds ]; then
            # Timeout reached, kill the test
            kill -TERM $pid 2>/dev/null
            sleep 2
            kill -KILL $pid 2>/dev/null
            return 124  # timeout exit code
        fi
        sleep 1
        ((count++))
    done
    
    # Get exit code
    wait $pid
    return $?
}

# Read the first MAX_TESTS tests from the file
echo "Reading first $MAX_TESTS tests from $TEST_FILE..."
TESTS=()
while IFS= read -r line; do
    # Skip empty lines and comments
    if [[ -n "$line" ]] && [[ ! "$line" =~ ^# ]]; then
        TESTS+=("$line")
        if [ ${#TESTS[@]} -ge $MAX_TESTS ]; then
            break
        fi
    fi
done < "$TEST_FILE"

echo "Will run ${#TESTS[@]} tests with ${TEST_TIMEOUT}s timeout each"
echo ""

# Process each test
for TEST_NAME in "${TESTS[@]}"; do
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo "[$TOTAL_TESTS/${#TESTS[@]}] Running: $TEST_NAME"
    echo "Test $TOTAL_TESTS: $TEST_NAME" >> "$REPORT_FILE"
    echo "----------------------------------------" >> "$REPORT_FILE"
    
    # Run the test with timeout
    START_TIME=$(date +%s)
    run_test_with_timeout "$TEST_NAME" "test_output_${TOTAL_TESTS}.log" $TEST_TIMEOUT
    EXIT_CODE=$?
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    # Check result and update counters
    if [[ $EXIT_CODE -eq 0 ]]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        STATUS="PASSED"
        echo "  ✓ PASSED (${DURATION}s)"
        echo "Status: PASSED" >> "$REPORT_FILE"
    elif [[ $EXIT_CODE -eq 124 ]]; then
        TIMEOUT_TESTS=$((TIMEOUT_TESTS + 1))
        STATUS="TIMEOUT"
        echo "  ⏱ TIMEOUT (${TEST_TIMEOUT}s exceeded)"
        echo "Status: TIMEOUT (exceeded ${TEST_TIMEOUT}s)" >> "$REPORT_FILE"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        STATUS="FAILED"
        echo "  ✗ FAILED (${DURATION}s, exit code: $EXIT_CODE)"
        echo "Status: FAILED (exit code: $EXIT_CODE)" >> "$REPORT_FILE"
    fi
    
    # Extract key information from log
    if [[ $EXIT_CODE -ne 0 ]]; then
        echo "Error summary:" >> "$REPORT_FILE"
        # Look for common error patterns
        if grep -q "TEST-UNEXPECTED-FAIL" "test_output_${TOTAL_TESTS}.log" 2>/dev/null; then
            grep "TEST-UNEXPECTED-FAIL" "test_output_${TOTAL_TESTS}.log" | head -5 >> "$REPORT_FILE"
        elif grep -q "ERROR" "test_output_${TOTAL_TESTS}.log" 2>/dev/null; then
            grep -E "(ERROR|FAIL)" "test_output_${TOTAL_TESTS}.log" | head -5 >> "$REPORT_FILE"
        else
            tail -20 "test_output_${TOTAL_TESTS}.log" 2>/dev/null | head -5 >> "$REPORT_FILE" || echo "  No log output captured" >> "$REPORT_FILE"
        fi
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
echo "Timed out: $TIMEOUT_TESTS"
echo ""

# Add summary to report
echo "=================================" >> "$REPORT_FILE"
echo "SUMMARY" >> "$REPORT_FILE"
echo "=================================" >> "$REPORT_FILE"
echo "Total tests run: $TOTAL_TESTS" >> "$REPORT_FILE"
echo "Passed: $PASSED_TESTS" >> "$REPORT_FILE"
echo "Failed: $FAILED_TESTS" >> "$REPORT_FILE"
echo "Timed out: $TIMEOUT_TESTS" >> "$REPORT_FILE"

if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=1; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)
    echo "Success rate: ${SUCCESS_RATE}%" >> "$REPORT_FILE"
else
    echo "Success rate: N/A (no tests run)" >> "$REPORT_FILE"
fi

echo "Report saved to: $REPORT_FILE"
echo "Individual test logs saved as: test_output_*.log"

# List failed tests for easy re-run
if [ $FAILED_TESTS -gt 0 ] || [ $TIMEOUT_TESTS -gt 0 ]; then
    echo ""
    echo "Failed/timed out tests:" >> "$REPORT_FILE"
    echo ""
    echo "Failed/timed out tests:"
    i=0
    for TEST_NAME in "${TESTS[@]}"; do
        i=$((i + 1))
        if grep -q "Status: \(FAILED\|TIMEOUT\)" <(sed -n "/Test $i:/,/^$/p" "$REPORT_FILE"); then
            echo "  $TEST_NAME"
            echo "  $TEST_NAME" >> "$REPORT_FILE"
        fi
    done
fi