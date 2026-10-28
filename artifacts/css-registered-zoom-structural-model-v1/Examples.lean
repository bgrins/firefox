import Structural

namespace RegisteredZoom.Structural.Examples

abbrev V := Value Nat Nat Nat Nat

def specimen : V :=
  .listCons
    (.transform 7 (.listCons (.lengthPercentage 10 25) (.listCons (.opaque 90) .listNil)))
    (.listCons
      (.image 8 (.math 3 (.length 6) (.listCons (.color 40) (.listCons (.percentage 50) .listNil))))
      .listNil)

def doubled : V :=
  .listCons
    (.transform 7 (.listCons (.lengthPercentage 20 25) (.listCons (.opaque 90) .listNil)))
    (.listCons
      (.image 8 (.math 3 (.length 12) (.listCons (.color 40) (.listCons (.percentage 50) .listNil))))
      .listNil)

example : mapLengths (fun n => n * 2) specimen = doubled := by decide +kernel
example : mapLengths (fun n => n / 2) doubled = specimen := by decide +kernel
example : nonLengths doubled = nonLengths specimen := by decide +kernel
example : (mapLengths (fun n => n * 2) (.percentage 50 : V)) = .percentage 50 := by decide +kernel
example : (mapLengths (fun n => n * 2) (.color 40 : V)) = .color 40 := by decide +kernel
example : (mapLengths (fun n => n * 2) (.opaque 90 : V)) = .opaque 90 := by decide +kernel

def wrongPercentage (length percentage : Nat) : V := .lengthPercentage (length * 2) (percentage * 2)
def wrongColor (color : Nat) : V := .color (color * 2)
def skippedImage (kind : Nat) (arguments : V) : V := .image kind arguments

end RegisteredZoom.Structural.Examples
