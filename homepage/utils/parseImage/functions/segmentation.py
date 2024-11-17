from numpy import ndarray
from onnxtr.models import ocr_predictor

model = ocr_predictor(
    det_arch="fast_base",  # detection architecture
    reco_arch="vitstr_base",  # recognition architecture
    det_bs=2,  # detection batch size
    reco_bs=512,  # recognition batch size
)


def getText(image: ndarray):
    # Analyze
    result = model([image])
    print(result.export().get("pages", [{"blocks": []}])[0].get("blocks", []))
