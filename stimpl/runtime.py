from typing import Any, Tuple, Optional

from stimpl.expression import *
from stimpl.types import *
from stimpl.errors import *

"""
Interpreter State
"""


class State(object):
    def __init__(self, variable_name: str, variable_value: Expr, variable_type: Type, next_state: 'State') -> None:
        self.variable_name = variable_name
        self.value = (variable_value, variable_type)
        self.next_state = next_state

    def copy(self) -> 'State':
        variable_value, variable_type = self.value
        return State(self.variable_name, variable_value, variable_type, self.next_state)

    def set_value(self, variable_name, variable_value, variable_type):
        return State(variable_name, variable_value, variable_type, self)

    def get_value(self, variable_name) -> Any:
        """ TODO: Implement. """
        #Returns a tuple whose first element is the variable value and whose second element is the variable type
        #if the variable is not defined in the current state, get it in the next state
        if self.variable_name == variable_name:
            return self.value
        else:
            return self.next_state.get_value(variable_name)

    def __repr__(self) -> str:
        return f"{self.variable_name}: {self.value}, " + repr(self.next_state)


class EmptyState(State):
    def __init__(self):
        pass

    def copy(self) -> 'EmptyState':
        return EmptyState()

    def get_value(self, variable_name) -> None:
        return None

    def __repr__(self) -> str:
        return ""


"""
Main evaluation logic!
"""


def evaluate(expression: Expr, state: State) -> Tuple[Optional[Any], Type, State]:
    match expression:
        case Ren():
            return (None, Unit(), state)

        case IntLiteral(literal=l):
            return (l, Integer(), state)

        case FloatingPointLiteral(literal=l):
            return (l, FloatingPoint(), state)

        case StringLiteral(literal=l):
            return (l, String(), state)

        case BooleanLiteral(literal=l):
            return (l, Boolean(), state)

        case Print(to_print=to_print):
            printable_value, printable_type, new_state = evaluate(
                to_print, state)

            match printable_type:
                case Unit():
                    print("Unit")
                case _:
                    print(f"{printable_value}")

            return (printable_value, printable_type, new_state)

        case Sequence(exprs=exprs) | Program(exprs=exprs):
            """ TODO: Implement. """
            #The value and type of a sequence of expressions are the value and type of the final expression in the sequence
            for i in range(len(exprs)):
                value_result, value_type, state = evaluate(exprs[i], state)
            return (value_result, value_type, state)

        case Variable(variable_name=variable_name):
            value = state.get_value(variable_name)
            if value == None:
                raise InterpSyntaxError(
                    f"Cannot read from {variable_name} before assignment.")
            variable_value, variable_type = value
            return (variable_value, variable_type, state)

        case Assign(variable=variable, value=value):

            value_result, value_type, new_state = evaluate(value, state)

            variable_from_state = new_state.get_value(variable.variable_name)
            _, variable_type = variable_from_state if variable_from_state else (
                None, None)

            if value_type != variable_type and variable_type != None:
                raise InterpTypeError(f"""Mismatched types for Assignment:
            Cannot assign {value_type} to {variable_type}""")

            new_state = new_state.set_value(
                variable.variable_name, value_result, value_type)
            return (value_result, value_type, new_state)

        case Add(left=left, right=right):
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            #Only matching typess of left and right can perform Add
            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Add:
            Cannot add {left_type} to {right_type}""")

            #Perform Add when left and right are of the same type
            match left_type:
                case Integer() | String() | FloatingPoint():
                    result = left_result + right_result
                case _:
                    raise InterpTypeError(f"""Cannot add {left_type}s""")

            return (result, left_type, new_state)

        case Subtract(left=left, right=right):
            """ TODO: Implement. """
            #Get the left and right tuples
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            #Only matching typess of left and right can perform the operation
            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Subtract:
            Cannot subtract {left_type} to {right_type}""")

            #Perform the operation when left and right are of the same type (only on operands of integer and floating-point types)
            match left_type:
                case Integer() | FloatingPoint():
                    result = left_result - right_result
                case _:
                    raise InterpTypeError(f"""Cannot subtract {left_type}s""")

            return (result, left_type, new_state)

        case Multiply(left=left, right=right):
            """ TODO: Implement. """
            #Get the left and right tuples
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            #Only matching typess of left and right can perform the operation
            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Multiply:
            Cannot multiply {left_type} to {right_type}""")

            #Perform the operation when left and right are of the same type (only on operands of integer and floating-point types)
            match left_type:
                case Integer() | FloatingPoint():
                    result = left_result * right_result
                case _:
                    raise InterpTypeError(f"""Cannot multiply {left_type}s""")

            return (result, left_type, new_state)


        case Divide(left=left, right=right):
            """ TODO: Implement. """
            #Get the left and right tuples
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            #Only matching typess of left and right can perform the operation
            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Divide:
            Cannot divide {left_type} to {right_type}""")
            
            #Perform the operation when left and right are of the same type
            match left_type:
                #Semantics: The divide operator performs integer division when its parameters are integers
                case Integer():
                    #Semantics: An attempt to divide by zero (either floating-point or integer) raises an InterpMathError.
                    if right_result == 0:
                        raise InterpMathError(f"""Cannot perform divide by {right_result}""")
                    else:
                        result = left_result // right_result
                case FloatingPoint():
                    if right_result == 0.0:
                        raise InterpMathError(f"""Cannot perform divide by {right_result}""")
                    else:
                        result = left_result / right_result
                case _:
                    raise InterpTypeError(f"""Cannot divide {left_type}s""")

            return (result, left_type, new_state)


        case And(left=left, right=right):
            #Get the left and right tuples
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)
            #Compare the type of left and right tuples
            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for And:
            Cannot perform logical and {left_type} to {right_type}""")
            #Perform logical operator on same type tuples
            match left_type:
                case Boolean():
                    result = left_value and right_value
                case _:
                    raise InterpTypeError(
                        "Cannot perform logical AND on non-boolean operands.")

            return (result, left_type, new_state)

        case Or(left=left, right=right):
            """ TODO: Implement. """
            #Get the left and right tuples
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)
            
            #Compare operands of the same type
            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Or:
            Cannot perform logical or {left_type} to {right_type}""")
            #Perform logical operator on same type tuples
            match left_type:
                case Boolean():
                    result = left_value or right_value
                case _:
                    raise InterpTypeError(
                        "Cannot perform logical OR on non-boolean operands.")
            return (result, left_type, new_state)

        case Not(expr=expr):
            """ TODO: Implement. """
            #Get the value, type and state of the expr
            expr_value, expr_type, new_state = evaluate(expr, state)

            match expr_type:
                case Boolean():
                    result = not(expr_value) #Perform not on the expr_value
                case _:
                    raise InterpTypeError("Cannot perform logical NOT on non-boolean operands.")
            return (result, expr_type, new_state)


        case If(condition=condition, true=true, false=false):
            """ TODO: Implement. """
            #Get the value, type and state of the condition
            condition_value, condition_type, new_state = evaluate(condition, state)

            match condition_type:
                case Boolean():
                    #if condition_value = true
                    if (condition_value):
                        true_result, true_type, new_state = evaluate(true, new_state)
                        return (true_result, true_type, new_state)
                    else:
                        false_result, false_type, new_state = evaluate(false, new_state)
                        return (false_result, false_type, new_state)
                case _:
                    raise InterpTypeError("Cannot perform logical IF on non-boolean operands.")



        case Lt(left=left, right=right):
            #Get the left and right tuples
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Lt:
            Cannot compare {left_type} to {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value < right_value
                case Unit():
                    result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform < on {left_type} type.")

            return (result, Boolean(), new_state)

        case Lte(left=left, right=right):
            """ TODO: Implement. """
            #Get the left and right tuples
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Lte:
            Cannot compare {left_type} to {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value <= right_value
                case Unit():
                    result = True
                case _:
                    raise InterpTypeError(
                        f"Cannot perform <= on {left_type} type.")

            return (result, Boolean(), new_state)


        case Gt(left=left, right=right):
            """ TODO: Implement. """
            #Get the left and right tuples
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Gt:
            Cannot compare {left_type} to {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value > right_value
                case Unit():
                    result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform > on {left_type} type.")

            return (result, Boolean(), new_state)

        case Gte(left=left, right=right):
            """ TODO: Implement. """
            #Get the left and right tuples
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Gte:
            Cannot compare {left_type} to {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value >= right_value
                case Unit():
                    result = True
                case _:
                    raise InterpTypeError(
                        f"Cannot perform >= on {left_type} type.")

            return (result, Boolean(), new_state)


        case Eq(left=left, right=right):
            """ TODO: Implement. """
            #Get the left and right tuples
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Eq:
            Cannot compare {left_type} to {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value == right_value
                case Unit():
                    result = True
                case _:
                    raise InterpTypeError(
                        f"Cannot perform == on {left_type} type.")

            return (result, Boolean(), new_state)

        case Ne(left=left, right=right):
            """ TODO: Implement. """
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Ne:
            Cannot compare {left_type} to {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value != right_value
                case Unit():
                    result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform != on {left_type} type.")

            return (result, Boolean(), new_state)

        case While(condition=condition, body=body):
            """ TODO: Implement. """
            condition_value, condition_type, new_state = evaluate(condition, state)
            
            match condition_type:
                case Boolean():
                    #Perform while when conditon_value == True
                    while (condition_value):
                        body_value, body_type, new_state = evaluate(body, new_state) #The body is evaluated, then the condition's state is updated if appropriate
                        condition_value, condition_type, new_state = evaluate(condition, new_state) #The condition is evaluated again
                    return (False, Boolean(), new_state) #The value and type of a while loop are false and boolean
                case _:
                    raise InterpTypeError(f"Cannot evaluate on non-boolean conditional")
        case _:
            raise InterpSyntaxError("Unhandled!")
    pass
def run_stimpl(program, debug=False):
    state = EmptyState()
    program_value, program_type, program_state = evaluate(program, state)

    if debug:
        print(f"program: {program}")
        print(f"final_value: ({program_value}, {program_type})")
        print(f"final_state: {program_state}")

    return program_value, program_type, program_state
