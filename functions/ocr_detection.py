# mac_ocr.py
import sys
from pathlib import Path

# PyObjC imports
from Foundation import NSURL
import Quartz
import Vision

def _load_cgimage(path: str):
    """Load image from disk into a CoreGraphics CGImageRef."""
    url = NSURL.fileURLWithPath_(str(path))
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    if not src:
        raise FileNotFoundError(f"Can't open image {path}")
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    if not img:
        raise RuntimeError("Failed to create CGImage")
    return img

def ocr_mac(path: str, recognition_level: str = "accurate", languages: list | None = None, use_language_correction: bool = True):
    """
    Perform OCR using macOS Vision framework.
    - recognition_level: "accurate" or "fast"
    - languages: list of BCP-47 language tags like ["en-US","hi-IN"] or None to auto-detect
    Returns recognized text (string).
    """
    # load image
    cgimg = _load_cgimage(path)

    # completion handler called by Vision request
    results_container = {"text": []}
    def completion_handler(request, error):
        if error is not None:
            # in PyObjC error will be an NSError object or None
            results_container["error"] = error
            return
        observations = request.results()
        if not observations:
            return
        # observations are VNRecognizedTextObservation objects
        lines = []
        for obs in observations:
            # topCandidates_(n) returns an NSArray of VNRecognizedText objects
            candidates = obs.topCandidates_(1)
            if len(candidates) > 0:
                # .string() is the actual recognized text
                lines.append(str(candidates[0].string()))
        results_container["text"] = lines

    # create request
    req = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(completion_handler)

    # set options
    rl = Vision.VNRequestTextRecognitionLevelAccurate if recognition_level == "accurate" else Vision.VNRequestTextRecognitionLevelFast
    req.setRecognitionLevel_(rl)
    req.setUsesLanguageCorrection_(bool(use_language_correction))

    if languages:
        # languages should be an NSArray of language tags
        from Foundation import NSArray
        req.setRecognitionLanguages_(NSArray.arrayWithArray_(languages))

    # create handler and perform
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(cgimg, None)
    success, err = handler.performRequests_error_([req], None)
    if not success:
        raise RuntimeError(f"Vision request failed: {err}")

    # join lines; Vision returns words/lines in reading order for many images
    text_lines = results_container.get("text", [])
    return "\n".join(text_lines)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mac_ocr.py /path/to/image.jpg")
        sys.exit(1)
    img_path = sys.argv[1]
    print("Recognizing text ...")
    txt = ocr_mac(img_path, recognition_level="accurate", languages=["en-US"])
    print("---- OCR output ----")
    print(txt)
