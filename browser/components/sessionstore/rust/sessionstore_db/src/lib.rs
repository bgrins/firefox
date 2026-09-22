/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

//! Implements `mozISessionStoreDatabase`, which stores session restore state
//! as rows of JSON fragments in a SQLite database. The caller opens the
//! connection; every operation then runs, in order, as a task on the
//! connection's own thread.

mod assemble;
mod batch;
mod error;
mod export;
mod schema;

use std::{cell::RefCell, ffi::c_void, mem, ptr, sync::Mutex};

use moz_task::{Task, TaskRunnable, ThreadPtrHandle, ThreadPtrHolder};
use nserror::{nsresult, NS_ERROR_NO_INTERFACE, NS_OK};
use nsstring::{nsACString, nsCString};
use storage::Conn;
use thin_vec::ThinVec;
use xpcom::{
    interfaces::{
        mozISessionStoreDatabaseCallback, mozIStorageAsyncConnection, mozIStorageConnection,
    },
    nsIID, xpcom, xpcom_method, RefPtr, XpCom,
};

use crate::error::{Error, Result};

#[no_mangle]
pub unsafe extern "C" fn NS_NewSessionStoreDatabase(
    iid: &nsIID,
    result: *mut *mut c_void,
) -> nsresult {
    *result = ptr::null_mut();
    SessionStoreDatabase::new().QueryInterface(iid, result)
}

#[xpcom(implement(mozISessionStoreDatabase), nonatomic)]
pub struct SessionStoreDatabase {
    conn: RefCell<Option<Conn>>,
}

impl SessionStoreDatabase {
    fn new() -> RefPtr<SessionStoreDatabase> {
        SessionStoreDatabase::allocate(InitSessionStoreDatabase {
            conn: RefCell::default(),
        })
    }

    xpcom_method!(
        init => Init(
            connection: *const mozIStorageAsyncConnection,
            callback: *const mozISessionStoreDatabaseCallback
        )
    );
    fn init(
        &self,
        connection: &mozIStorageAsyncConnection,
        callback: &mozISessionStoreDatabaseCallback,
    ) -> std::result::Result<(), nsresult> {
        let connection = connection
            .query_interface::<mozIStorageConnection>()
            .ok_or(NS_ERROR_NO_INTERFACE)?;
        let conn = Conn::wrap(connection);
        self.conn.replace(Some(conn.clone()));
        dispatch("SessionStoreDatabase::Init", conn, Operation::Init, callback)
    }

    xpcom_method!(
        read => Read(validate: bool, callback: *const mozISessionStoreDatabaseCallback)
    );
    fn read(
        &self,
        validate: bool,
        callback: &mozISessionStoreDatabaseCallback,
    ) -> std::result::Result<(), nsresult> {
        let conn = self.conn()?;
        dispatch(
            "SessionStoreDatabase::Read",
            conn,
            Operation::Read { validate },
            callback,
        )
    }

    xpcom_method!(
        write => Write(
            ops: *const ThinVec<nsCString>,
            callback: *const mozISessionStoreDatabaseCallback
        )
    );
    fn write(
        &self,
        ops: &ThinVec<nsCString>,
        callback: &mozISessionStoreDatabaseCallback,
    ) -> std::result::Result<(), nsresult> {
        let conn = self.conn()?;
        let ops = batch::parse(ops)?;
        dispatch(
            "SessionStoreDatabase::Write",
            conn,
            Operation::Write(ops),
            callback,
        )
    }

    xpcom_method!(
        export_json => ExportJSON(
            path: *const nsACString,
            tmp_path: *const nsACString,
            backup_path: *const nsACString,
            callback: *const mozISessionStoreDatabaseCallback
        )
    );
    fn export_json(
        &self,
        path: &nsACString,
        tmp_path: &nsACString,
        backup_path: &nsACString,
        callback: &mozISessionStoreDatabaseCallback,
    ) -> std::result::Result<(), nsresult> {
        let conn = self.conn()?;
        dispatch(
            "SessionStoreDatabase::ExportJSON",
            conn,
            Operation::Export {
                path: path.to_utf8().into_owned(),
                tmp_path: tmp_path.to_utf8().into_owned(),
                backup_path: backup_path.to_utf8().into_owned(),
            },
            callback,
        )
    }

    xpcom_method!(reset => Reset());
    fn reset(&self) -> std::result::Result<(), nsresult> {
        mem::drop(self.conn.borrow_mut().take());
        Ok(())
    }

    fn conn(&self) -> Result<Conn> {
        self.conn.borrow().clone().ok_or(Error::NotInitialized)
    }
}

enum Operation {
    Init,
    Read {
        validate: bool,
    },
    Write(Vec<batch::Op>),
    Export {
        path: String,
        tmp_path: String,
        backup_path: String,
    },
}

fn dispatch(
    name: &'static str,
    conn: Conn,
    operation: Operation,
    callback: &mozISessionStoreDatabaseCallback,
) -> std::result::Result<(), nsresult> {
    let thread = conn.thread()?;
    let task = DatabaseTask {
        conn,
        operation: Mutex::new(Some(operation)),
        callback: ThreadPtrHolder::new(
            c"mozISessionStoreDatabaseCallback",
            RefPtr::new(callback),
        )?,
        result: Mutex::new(Err(Error::DidNotRun)),
    };
    TaskRunnable::new(name, Box::new(task))?.dispatch(&thread)
}

struct DatabaseTask {
    conn: Conn,
    operation: Mutex<Option<Operation>>,
    callback: ThreadPtrHandle<mozISessionStoreDatabaseCallback>,
    result: Mutex<Result<nsCString>>,
}

impl DatabaseTask {
    fn run_operation(&self) -> Result<nsCString> {
        let operation = self.operation.lock().unwrap().take();
        match operation.ok_or(Error::DidNotRun)? {
            Operation::Init => {
                schema::init(&self.conn).map(|version| nsCString::from(version.to_string()))
            }
            Operation::Read { validate } => assemble::read(&self.conn, validate),
            Operation::Write(ops) => batch::apply(&self.conn, ops).map(|()| nsCString::new()),
            Operation::Export {
                path,
                tmp_path,
                backup_path,
            } => export::export(&self.conn, &path, &tmp_path, &backup_path),
        }
    }
}

impl Task for DatabaseTask {
    fn run(&self) {
        *self.result.lock().unwrap() = self.run_operation();
    }

    fn done(&self) -> std::result::Result<(), nsresult> {
        let callback = self.callback.get().unwrap();
        let result = mem::replace(&mut *self.result.lock().unwrap(), Err(Error::DidNotRun));
        match result {
            Ok(value) => unsafe { callback.OnSuccess(&*value) },
            Err(err) => {
                let message = nsCString::from(err.to_string());
                unsafe { callback.OnError(err.into(), &*message) }
            }
        }
        .to_result()
    }
}
