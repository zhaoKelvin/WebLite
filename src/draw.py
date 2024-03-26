import skia
from utils import parse_color

class DrawLine:
    def __init__(self, x1, y1, x2, y2, color, thickness):
        self.rect = skia.Rect.MakeLTRB(x1, y1, x2, y2)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.thickness = thickness

    def execute(self, canvas):
        path = skia.Path().moveTo(self.x1, self.y1).lineTo(self.x2, self.y2)
        paint = skia.Paint(Color=parse_color(self.color))
        paint.setStyle(skia.Paint.kStroke_Style)
        paint.setStrokeWidth(self.thickness)
        canvas.drawPath(path, paint)

class DrawOutline:
    def __init__(self, rect, color, thickness):
        self.rect = rect
        self.color = color
        self.thickness = thickness

    def execute(self, canvas):
        paint = skia.Paint()
        paint.setStyle(skia.Paint.kStroke_Style)
        paint.setStrokeWidth(self.thickness)
        paint.setColor(parse_color(self.color))
        canvas.drawRect(self.rect, paint)

class DrawRect:
    def __init__(self, rect, color):
        self.rect = rect
        self.color = color
        
    def execute(self, canvas):
        paint = skia.Paint()
        paint.setColor(parse_color(self.color))
        canvas.drawRect(self.rect, paint)
    
    def __repr__(self):
        return "DrawRect(top={} left={} bottom={} right={} color={})".format(
            self.rect.top(), self.rect.left(), self.rect.bottom(),
            self.rect.right(), self.color)
        
class DrawRRect:
    def __init__(self, rect, radius, color):
        self.rect = rect
        self.rrect = skia.RRect.MakeRectXY(rect, radius, radius)
        self.color = color

    def execute(self, canvas):
        sk_color = parse_color(self.color)
        canvas.drawRRect(self.rrect, paint=skia.Paint(Color=sk_color))
        
class DrawText:
    def __init__(self, x1, y1, text, font, color):
        self.left = x1
        self.top = y1
        self.right = x1 + font.measureText(text)
        self.bottom = y1 - font.getMetrics().fAscent + font.getMetrics().fDescent
        self.rect = skia.Rect.MakeLTRB(x1, y1, self.right, self.bottom)
        self.font = font
        self.text = text
        self.color = color
        
    def execute(self, canvas):
        paint = skia.Paint(
            AntiAlias=True, Color=parse_color(self.color))
        baseline = self.top - self.font.getMetrics().fAscent
        canvas.drawString(self.text, float(self.left), baseline, self.font, paint)