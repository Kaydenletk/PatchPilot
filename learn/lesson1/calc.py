def add(a: int, b: int) -> int:
     return a + b

def safe_divide(a: float, b: float) -> float | None:
     if b == 0:
          return None
     return a / b