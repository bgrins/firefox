    let phase = "setup";
    let sequence = 0;
    const mark = stage => dump("CSS_SIZEFORMS_STAGE " + JSON.stringify({mode, phase, sequence: ++sequence, stage}) + "\n");
    const read = (stage, operation) => {
      mark(stage + ":before");
      const value = operation();
      mark(stage + ":after");
      return value;
    };
    mark("body:start");
