--- HEAD/layout/generic/StickyScrollContainer.cpp
+++ after-recorded-reversals/layout/generic/StickyScrollContainer.cpp
@@ -195,34 +195,38 @@
   nsMargin sfPadding = scrolledFrame->GetUsedPadding();
   nsPoint sfOffset = aFrame->GetParent()->GetOffsetTo(scrolledFrame);
   nsSize sfSize = GetScrollContainerSize(mScrollContainerFrame);
-  StyleDirection direction = cbFrame->StyleVisibility()->mDirection;
-  nsMargin effectiveOffsets = *computedOffsets;
-
-  if (computedOffsets->top != NS_AUTOOFFSET &&
+  WritingMode writingMode = cbFrame->GetWritingMode();
+  nsMargin effectiveOffsets(
+      computedOffsets->top == NS_AUTOOFFSET ? 0 : computedOffsets->top,
+      computedOffsets->right == NS_AUTOOFFSET ? 0 : computedOffsets->right,
+      computedOffsets->bottom == NS_AUTOOFFSET ? 0 : computedOffsets->bottom,
+      computedOffsets->left == NS_AUTOOFFSET ? 0 : computedOffsets->left);
+
+  if (computedOffsets->top != NS_AUTOOFFSET ||
       computedOffsets->bottom != NS_AUTOOFFSET) {
     // Decrease the effective end-edge inset of the sticky view rectangle
     // when its height is less than the height of the border-box of the sticky
     // box.
-    nscoord stickyViewHeight = sfSize.height - computedOffsets->TopBottom();
+    nscoord stickyViewHeight = sfSize.height - effectiveOffsets.TopBottom();
     if (rect.height > stickyViewHeight) {
       nscoord delta = rect.height - stickyViewHeight;
-      effectiveOffsets.bottom -= delta;
+      effectiveOffsets.Side(writingMode.PhysicalSide(
+          writingMode.IsVertical() ? LogicalSide::IEnd : LogicalSide::BEnd)) -=
+          delta;
     }
   }
 
-  if (computedOffsets->left != NS_AUTOOFFSET &&
+  if (computedOffsets->left != NS_AUTOOFFSET ||
       computedOffsets->right != NS_AUTOOFFSET) {
     // Decrease the effective end-edge inset of the sticky view rectangle
     // when its width is less than the width of the border-box of the sticky
     // box.
-    nscoord stickyViewWidth = sfSize.width - computedOffsets->LeftRight();
+    nscoord stickyViewWidth = sfSize.width - effectiveOffsets.LeftRight();
     if (rect.width > stickyViewWidth) {
       nscoord delta = rect.width - stickyViewWidth;
-      if (direction == StyleDirection::Ltr) {
-        effectiveOffsets.right -= delta;
-      } else {
-        effectiveOffsets.left -= delta;
-      }
+      effectiveOffsets.Side(writingMode.PhysicalSide(
+          writingMode.IsVertical() ? LogicalSide::BEnd : LogicalSide::IEnd)) -=
+          delta;
     }
   }
 
