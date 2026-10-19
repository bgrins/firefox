if (colSpan > 1) {
            // If a column-spanning cell is in the first row, split up
            // the space evenly.  (XXX This isn't quite right if some of
            // the columns it's in have specified iSizes.  Should we
            // care?)
            nscoord spacing = mTableFrame->GetColSpacing(col);
            colISize = ((colISize + spacing) / colSpan) - spacing;
            if (colISize < 0) {
              colISize = 0;
            }
          }
