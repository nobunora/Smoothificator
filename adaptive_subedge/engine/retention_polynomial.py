"""Bounded exact polynomial grammar for user-calibrated dimension retention."""
import ast
from functools import lru_cache
from fractions import Fraction as F
import re

DEFAULT_RETENTION_EXPRESSION='1-(6*t**5-15*t**4+10*t**3)'


def _bounded(coefficients):
    coefficients=list(coefficients)
    while len(coefficients)>1 and coefficients[-1]==0:coefficients.pop()
    if len(coefficients)>13 or any(max(v.numerator.bit_length(),v.denominator.bit_length())>128 for v in coefficients):
        raise ValueError('retention-polynomial-resource-limit')
    return tuple(coefficients)


def _add(left,right,sign=1):
    return _bounded((left[i] if i<len(left) else F(0))+sign*(right[i] if i<len(right) else F(0)) for i in range(max(len(left),len(right))))


def _multiply(left,right):
    if len(left)+len(right)-2>12:raise ValueError('retention-polynomial-degree-limit')
    out=[F(0)]*(len(left)+len(right)-1)
    for i,a in enumerate(left):
        for j,b in enumerate(right):
            out[i+j]+=a*b
            _bounded(out)
    return _bounded(out)


@lru_cache(maxsize=64)
def _retention_coefficients(expression):
    if type(expression) is not str or not 0<len(expression)<=512 or not expression.isascii():
        raise ValueError('invalid-retention-expression')
    try:tree=ast.parse(expression,mode='eval')
    except (SyntaxError,ValueError,RecursionError) as e:raise ValueError('invalid-retention-expression') from e
    if sum(1 for _ in ast.walk(tree))>128:raise ValueError('retention-expression-node-limit')
    def visit(node,depth=0):
        if depth>24:raise ValueError('retention-expression-depth-limit')
        if isinstance(node,ast.Name) and node.id=='t':return (F(0),F(1))
        if isinstance(node,ast.Constant) and type(node.value) in (int,float):
            literal=ast.get_source_segment(expression,node)
            if re.fullmatch(r'(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)',literal or '') is None:raise ValueError('invalid-retention-literal')
            return _bounded((F(literal),))
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            part=visit(node.operand,depth+1)
            return _bounded(v*(-1 if isinstance(node.op,ast.USub) else 1) for v in part)
        if isinstance(node,ast.BinOp):
            left=visit(node.left,depth+1)
            if isinstance(node.op,ast.Pow):
                if not isinstance(node.right,ast.Constant) or type(node.right.value) is not int or not 0<=node.right.value<=12:raise ValueError('invalid-retention-power')
                out=(F(1),)
                for _ in range(node.right.value):out=_multiply(out,left)
                return out
            right=visit(node.right,depth+1)
            if isinstance(node.op,ast.Add):return _add(left,right)
            if isinstance(node.op,ast.Sub):return _add(left,right,-1)
            if isinstance(node.op,ast.Mult):return _multiply(left,right)
            if isinstance(node.op,ast.Div) and len(right)==1 and right[0]!=0:return _bounded(v/right[0] for v in left)
        raise ValueError('unsupported-retention-expression')
    coefficients=visit(tree.body)
    if coefficients[0]!=1 or sum(coefficients,F(0))!=0:raise ValueError('retention-endpoints-must-be-one-and-zero')
    return coefficients


def retention_coefficients(expression):
    if type(expression) is not str or not 0<len(expression)<=512 or not expression.isascii():
        raise ValueError('invalid-retention-expression')
    return _retention_coefficients(expression)


def retention_for_t(expression,t):
    if type(t) is not F or not 0<=t<=1 or max(t.numerator.bit_length(),t.denominator.bit_length())>128:raise ValueError('invalid-retention-coordinate')
    out=F(0)
    for coefficient in reversed(retention_coefficients(expression)):out=out*t+coefficient
    return max(F(0),min(F(1),out))
