window.scopeResults = [];
add_result_callback(test => {
  window.scopeResults.push({name: test.name, status: test.status,
    message: test.message, stack: test.stack});
});
add_completion_callback((tests, status) => {
  window.scopeCompletion = {status: status.status, message: status.message,
    href: location.href, userAgent: navigator.userAgent,
    remainingFixtures: document.querySelectorAll('[id^="host-"]').length};
});
