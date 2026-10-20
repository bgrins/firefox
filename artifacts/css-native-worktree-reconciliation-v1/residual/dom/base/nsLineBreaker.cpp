--- HEAD/dom/base/nsLineBreaker.cpp
+++ after-recorded-reversals/dom/base/nsLineBreaker.cpp
@@ -403,7 +403,6 @@
       mTextItems.AppendElement(TextItem(aSink, wordStart, len, aFlags));
       // Ensure that the break-before for this word is written out
       offset = wordStart + 1;
-      UpdateCurrentWordLanguage(aHyphenationLanguage);
       break;
     }
   }
@@ -553,6 +552,8 @@
     }
 
     if (offset > 0) {
+      UpdateCurrentWordLanguage(aHyphenationLanguage);
+      mCurrentWordHyphenationLimits = mHyphenationLimits;
       mTextItems.AppendElement(TextItem(aSink, 0, offset, aFlags));
     }
 
@@ -660,6 +661,8 @@
       mTextItems.AppendElement(TextItem(aSink, wordStart, len, aFlags));
       // Ensure that the break-before for this word is written out
       offset = wordStart + 1;
+      UpdateCurrentWordLanguage(aHyphenationLanguage);
+      mCurrentWordHyphenationLimits = mHyphenationLimits;
       break;
     }
   }
