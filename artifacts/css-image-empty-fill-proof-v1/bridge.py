import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def between(text, start, end):
    assert text.count(start) == 1, start
    first = text.index(start)
    return text[first:text.index(end, first)]


def generate(candidate=True):
    for item in json.loads((ROOT / 'SOURCE-v1.json').read_text()):
        assert hashlib.sha256((ROOT / item['copy']).read_bytes()).hexdigest() == item['sha256']
    label = 'candidate' if candidate else 'original'
    source = (ROOT / f'source/{label}-nsCSSRendering.cpp').read_text()
    header = (ROOT / f'source/{label}-nsCSSRendering.h').read_text()
    renderer = (ROOT / f'source/{label}-nsImageRenderer.h').read_text()
    style = (ROOT / 'source/nsStyleStruct.h').read_text()
    result = (ROOT / 'source/ImgDrawResult.h').read_text()
    blocks = {
        'RESULT': between(result, 'enum class [[nodiscard]] ImgDrawResult', '\n/**\n * A struct used during painting'),
        'STATE': between(header, 'struct nsBackgroundLayerState {', '\nstruct nsCSSRendering {'),
        'READY': between(renderer, 'bool IsReady() const', '\n  const nsSize& GetSize()'),
        'IMAGE_FLAGS': between(renderer, '  enum {\n    FLAG_SYNC_DECODE_IMAGES', '\n  enum FitType'),
        'PARAMS': between(header, '  struct PaintBGParams {', '\n\n  static ImgDrawResult PaintStyleImageLayer('),
        'FLAGS': between(header, '  enum {\n    /**\n     * When this flag is passed', '\n\n  struct PaintBGParams'),
        'OPERATOR': between(header, '  static CompositionOp GetGFXCompositeMode(', '\n\n protected:'),
        'ITERATION': between(style, '#define NS_FOR_VISIBLE_IMAGE_LAYERS_BACK_TO_FRONT_WITH_RANGE', '\n};'),
    }
    prefix = (ROOT / 'adapter-prefix.cpp').read_text()
    for name, value in blocks.items():
        assert prefix.count('@@' + name + '@@') == 1
        prefix = prefix.replace('@@' + name + '@@', value)
    functions = [
        between(source, 'nsCSSRendering::PaintBGParams nsCSSRendering::PaintBGParams::ForAllLayers(', '\nImgDrawResult nsCSSRendering::PaintStyleImageLayer('),
        between(source, 'static CompositionOp DetermineCompositionOp(', '\nImgDrawResult nsCSSRendering::PaintStyleImageLayerWithSC('),
        between(source, 'nsBackgroundLayerState nsCSSRendering::PrepareImageLayer(', '\nnsRect nsCSSRendering::GetBackgroundLayerRect('),
        between(source, 'ImgDrawResult nsCSSRendering::PaintStyleImageLayerWithSC(', '\nImgDrawResult\nnsCSSRendering::BuildWebRenderDisplayItemsForStyleImageLayerWithSC('),
    ]
    return prefix + '\n'.join(functions) + (ROOT / 'adapter-suffix.cpp').read_text()
