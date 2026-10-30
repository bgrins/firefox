{
  "query": "WEB-ANIMATIONS-1#iteration-duration",
  "direction": "incoming",
  "matches": [
    {
      "spec": "WEB-ANIMATIONS-1",
      "anchor": "iteration-duration",
      "title": "iteration duration",
      "type": "definition",
      "resolution": "exact",
      "incoming": [
        {
          "spec": "CSS-ANIMATIONS-2",
          "anchor": "event-dispatch",
          "step_path": "3",
          "step_text": "The elapsed time is the result of evaluating (iteration boundary - iteration start) × iteration duration).",
          "call_site_id": "ref-for-iteration-duration②",
          "kind": "step"
        },
        {
          "spec": "WEB-ANIMATIONS-1",
          "anchor": "overall-progress",
          "step_path": "2",
          "step_text": "Calculate an initial value for overall progress based on the first matching condition below:",
          "call_site_id": "ref-for-iteration-duration①④",
          "kind": "step"
        },
        {
          "spec": "WEB-ANIMATIONS-1",
          "anchor": "overall-progress",
          "step_path": "2",
          "step_text": "Calculate an initial value for overall progress based on the first matching condition below:",
          "call_site_id": "ref-for-iteration-duration①⑤",
          "kind": "step"
        },
        {
          "spec": "WEB-ANIMATIONS-1",
          "anchor": "the-keyframeeffect-interface",
          "step_path": "2",
          "step_text": "Set the following properties of effect using the corresponding values of source: effect target, keyframes, composite operation, and all specified timing properties: start delay, end delay, fill mode, iteration start, iteration count, iteration duration, playback direction, and easing function.",
          "call_site_id": "ref-for-iteration-duration②⓪",
          "kind": "step"
        },
        {
          "spec": "WEB-ANIMATIONS-1",
          "anchor": "update-the-timing-properties-of-an-animation-effect",
          "step_path": "5",
          "step_text": "Assign each member that exists in input to the corresponding timing property of effect as follows: delay → start delay endDelay → end delay fill → fill mode iterationStart → iteration start iterations → iteration count duration → iteration duration direction → playback direction easing → easing function",
          "call_site_id": "ref-for-iteration-duration①⑧",
          "kind": "step"
        }
      ]
    }
  ]
}
