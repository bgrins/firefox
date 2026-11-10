/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

#[cfg(feature = "gecko-gtest")]
fn host_failure(message: String) {
    use std::ffi::CString;
    use std::os::raw::c_char;
    extern "C" {
        fn GTest_ExpectFailure(message: *const c_char);
    }
    let message = CString::new(message.replace('\0', "\\0")).unwrap();
    unsafe {
        GTest_ExpectFailure(message.as_ptr());
    }
}

#[cfg(feature = "gecko-gtest")]
macro_rules! assert {
    ($condition:expr $(,)?) => {
        if !$condition {
            crate::host_failure(format!(
                "{}:{}: {}",
                file!(),
                line!(),
                stringify!($condition)
            ));
            return;
        }
    };
}

#[cfg(feature = "gecko-gtest")]
macro_rules! assert_eq {
    ($left:expr, $right:expr $(,)?) => {
        match (&$left, &$right) {
            (left, right) if left != right => {
                crate::host_failure(format!(
                    "{}:{}: {:?} != {:?}",
                    file!(),
                    line!(),
                    left,
                    right
                ));
                return;
            },
            _ => {},
        }
    };
}

#[cfg(feature = "gecko-gtest")]
macro_rules! assert_ne {
    ($left:expr, $right:expr $(,)?) => {
        match (&$left, &$right) {
            (left, right) if left == right => {
                crate::host_failure(format!(
                    "{}:{}: values unexpectedly equal",
                    file!(),
                    line!()
                ));
                return;
            },
            _ => {},
        }
    };
}

pub use style::{gecko_bindings, properties, values};
#[cfg(any(test, feature = "gecko-gtest"))]
mod arithmetic_cases;
pub use style::deferred_animation_operations;
#[cfg(feature = "gecko-gtest")]
mod graph_cases;
#[cfg(feature = "gecko-gtest")]
mod metadata_cases;
#[cfg(feature = "gecko-gtest")]
mod rule_sample_cases;

#[cfg(feature = "gecko-gtest")]
#[no_mangle]
pub unsafe extern "C" fn Rust_RunAnimationOperationArenaCases(
    left: *mut gecko_bindings::structs::URLExtraData,
    right: *mut gecko_bindings::structs::URLExtraData,
) {
    if left.is_null() || right.is_null() {
        host_failure("missing real URLExtraData fixture".into());
        return;
    }
    let left = style::stylesheets::UrlExtraData::new(left);
    let right = style::stylesheets::UrlExtraData::new(right);
    graph_cases::run_all();
    arithmetic_cases::run_all();
    metadata_cases::run_all(&left, &right);
}

#[cfg(feature = "gecko-gtest")]
mod differential_cases;

#[cfg(feature = "gecko-gtest")]
mod endpoint_transition_cases;

#[cfg(feature = "gecko-gtest")]
mod owner_cases;

#[cfg(feature = "gecko-gtest")]
mod descriptor_bulk_cases;
