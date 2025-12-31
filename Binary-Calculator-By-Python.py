import tkinter as tk
from tkinter import ttk, font, messagebox
import math
import re

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("二进制计算器")
        self.root.geometry("525x700")
        self.root.resizable(False, False)
        
        self.mode = "standard"
        self.current_expression = ""
        self.current_base = 10
        self.angle_mode = "deg"
        self.last_operator = None
        self.logic_operator = None
        self.shift_operator = None
        
        self.base_buttons = {}
        self.disabled_buttons = []
        
        self.deg_btn = None
        self.rad_btn = None
        
        self.style = ttk.Style()
        self.style.configure('Bold.TButton', font=('Arial', 10, 'bold'))
        
        self.create_widgets()
        
    def create_widgets(self):
        self.base_display_frame = ttk.Frame(self.root)
        self.base_display_frame.pack(fill=tk.X, padx=10, pady=5)
        
        bases = [
            ("二进制 (Bin):", "bin_var"),
            ("八进制 (Oct):", "oct_var"),
            ("十进制 (Dec):", "dec_var"),
            ("十六进制 (Hex):", "hex_var")
        ]
        
        for i, (label_text, var_name) in enumerate(bases):
            frame = ttk.Frame(self.base_display_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=label_text, width=15).pack(side=tk.LEFT)
            var = tk.StringVar()
            setattr(self, var_name, var)
            ttk.Entry(frame, textvariable=var, state="readonly", width=25).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        mode_frame = ttk.Frame(self.root)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.standard_btn = ttk.Button(mode_frame, text="标准版", command=self.switch_to_standard)
        self.standard_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.programmer_btn = ttk.Button(mode_frame, text="程序员版", command=self.switch_to_programmer)
        self.programmer_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.display_var = tk.StringVar()
        self.display = ttk.Entry(self.root, textvariable=self.display_var, font=('Arial', 20), justify=tk.RIGHT)
        self.display.pack(fill=tk.X, padx=10, pady=10)
        self.display.config(state='readonly')
        
        self.buttons_frame = ttk.Frame(self.root)
        self.buttons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_standard_buttons()
    
    def switch_to_standard(self):
        self.mode = "standard"
        self.current_base = 10
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        self.create_standard_buttons()
        self.clear_display()
        self.update_base_display()
    
    def switch_to_programmer(self):
        self.mode = "programmer"
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        self.create_programmer_buttons()
        self.clear_display()
        self.update_base_display()
    
    def create_standard_buttons(self):
        buttons = [
            ('sin', 0, 0), ('cos', 0, 1), ('tan', 0, 2), ('AC', 0, 3), ('⌫', 0, 4),
            ('deg', 1, 0), ('rad', 1, 1), ('exp', 1, 2), ('log', 1, 3), ('ln', 1, 4),
            ('!', 2, 0), ('(', 2, 1), (')', 2, 2), ('%', 2, 3), ('/', 2, 4),
            ('^', 3, 0), ('7', 3, 1), ('8', 3, 2), ('9', 3, 3), ('*', 3, 4),
            ('√', 4, 0), ('4', 4, 1), ('5', 4, 2), ('6', 4, 3), ('-', 4, 4),
            ('π', 5, 0), ('1', 5, 1), ('2', 5, 2), ('3', 5, 3), ('+', 5, 4),
            ('e', 6, 0), ('±', 6, 1), ('0', 6, 2), ('.', 6, 3), ('=', 6, 4)
        ]
        
        for i in range(7):
            self.buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(5):
            self.buttons_frame.grid_columnconfigure(i, weight=1)
        
        for text, row, col in buttons:
            btn = ttk.Button(self.buttons_frame, text=text, 
                           command=lambda t=text: self.on_button_click(t))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            
            if text == 'deg':
                self.deg_btn = btn
            elif text == 'rad':
                self.rad_btn = btn
        
        self.update_angle_mode_buttons()
    
    def create_programmer_buttons(self):
        self.base_buttons.clear()
        self.disabled_buttons.clear()
        
        for i in range(8):
            self.buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(5):
            self.buttons_frame.grid_columnconfigure(i, weight=1)
        
        base_frame = ttk.Frame(self.buttons_frame)
        base_frame.grid(row=0, column=0, columnspan=5, sticky="nsew", padx=2, pady=2)
        
        base_names = ["二进制", "八进制", "十进制", "十六进制"]
        base_values = [2, 8, 10, 16]
        
        for i, (name, value) in enumerate(zip(base_names, base_values)):
            btn = ttk.Button(base_frame, text=name, 
                           command=lambda b=value: self.set_base(b))
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
            self.base_buttons[value] = btn
        
        buttons = [
            ('AND', 1, 0), ('OR', 1, 1), ('NOT', 1, 2), ('XOR', 1, 3), ('XNOR', 1, 4),
            ('A', 2, 0), ('<<', 2, 1), ('>>', 2, 2), ('AC', 2, 3), ('⌫', 2, 4),
            ('B', 3, 0), ('(', 3, 1), (')', 3, 2), ('%', 3, 3), ('/', 3, 4),
            ('C', 4, 0), ('7', 4, 1), ('8', 4, 2), ('9', 4, 3), ('*', 4, 4),
            ('D', 5, 0), ('4', 5, 1), ('5', 5, 2), ('6', 5, 3), ('-', 5, 4),
            ('E', 6, 0), ('1', 6, 1), ('2', 6, 2), ('3', 6, 3), ('+', 6, 4),
            ('F', 7, 0), ('±', 7, 1), ('0', 7, 2), ('.', 7, 3), ('=', 7, 4)
        ]
        
        self.programmer_buttons = {}
        for text, row, col in buttons:
            btn = ttk.Button(self.buttons_frame, text=text, 
                           command=lambda t=text: self.on_button_click(t))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            self.programmer_buttons[text] = btn
        
        self.set_base(10)
    
    def set_base(self, base):
        for b_val, btn in self.base_buttons.items():
            if b_val == base:
                btn.config(style='Bold.TButton')
            else:
                btn.config(style='TButton')
        
        old_base = self.current_base
        self.current_base = base
        
        self.update_button_states()
        
        if self.current_expression and self.mode == "programmer":
            try:
                expr = self.current_expression
                
                def convert_match(match):
                    num_str = match.group(0)
                    try:
                        if '.' in num_str:
                            decimal_val = float(num_str)
                        else:
                            decimal_val = int(num_str, old_base)
                        if isinstance(decimal_val, int):
                            return self.convert_base(decimal_val, base)
                        else:
                            return str(decimal_val)
                    except:
                        return num_str
                
                pattern = r'[0-9A-F\.]+' if old_base == 16 else r'[0-9\.]+'
                new_expr = re.sub(pattern, convert_match, expr, flags=re.IGNORECASE)
                
                self.current_expression = new_expr
                self.display_var.set(self.current_expression)
            except Exception as e:
                print(f"进制转换错误: {e}")
                self.clear_display()
        
        self.update_base_display()
    
    def update_button_states(self):
        if self.mode != "programmer":
            return
        
        for btn in self.disabled_buttons:
            btn.config(state='normal')
        self.disabled_buttons = []
        
        disabled_texts = []
        if self.current_base == 2:
            disabled_texts = ['2', '3', '4', '5', '6', '7', '8', '9', 
                             'A', 'B', 'C', 'D', 'E', 'F', '.']
        elif self.current_base == 8:
            disabled_texts = ['8', '9', 'A', 'B', 'C', 'D', 'E', 'F', '.']
        elif self.current_base == 10:
            disabled_texts = ['A', 'B', 'C', 'D', 'E', 'F']
        elif self.current_base == 16:
            disabled_texts = ['.']
        
        for text in disabled_texts:
            if text in self.programmer_buttons:
                self.programmer_buttons[text].config(state='disabled')
                self.disabled_buttons.append(self.programmer_buttons[text])
    
    def update_angle_mode_buttons(self):
        if self.deg_btn and self.rad_btn:
            if self.angle_mode == "deg":
                self.deg_btn.config(style='Bold.TButton')
                self.rad_btn.config(style='TButton')
            else:
                self.deg_btn.config(style='TButton')
                self.rad_btn.config(style='Bold.TButton')
    
    def on_button_click(self, text):
        if text == '=':
            self.calculate()
        elif text == 'AC':
            self.clear_display()
        elif text == '⌫':
            self.backspace()
        elif text == '±':
            self.toggle_sign()
        elif text == 'deg':
            self.angle_mode = "deg"
            self.update_angle_mode_buttons()
        elif text == 'rad':
            self.angle_mode = "rad"
            self.update_angle_mode_buttons()
        elif text in ['sin', 'cos', 'tan', 'log', 'ln', 'exp']:
            self.append_function(text)
        elif text in ['√', '!', '^']:
            self.append_operator(text)
        elif text in ['π', 'e']:
            self.append_constant(text)
        elif text in ['AND', 'OR', 'NOT', 'XOR', 'XNOR']:
            self.handle_logic_operator(text)
        elif text in ['<<', '>>']:
            self.handle_shift_operator(text)
        elif text == '%':
            self.handle_percent()
        else:
            self.append_to_expression(text)
            if self.mode == "standard":
                self.update_base_display()
    
    def append_function(self, func):
        if self.mode == "standard":
            self.current_expression += f"{func}("
        else:
            self.current_expression += func
        self.display_var.set(self.current_expression)
    
    def append_operator(self, operator):
        if not self.current_expression and operator not in ['-', '√']:
            return
        
        if self.current_expression and self.current_expression[-1] in '+-*/^':
            self.current_expression = self.current_expression[:-1]
        
        if operator == '√':
            self.current_expression += '√('
        else:
            self.current_expression += operator
        
        self.last_operator = operator
        self.display_var.set(self.current_expression)
    
    def handle_percent(self):
        if not self.current_expression:
            return
        
        try:
            expr = self.current_expression
            match = re.search(r'([\d\.]+)$', expr)
            if match:
                num = float(match.group(1))
                percent = num / 100
                self.current_expression = expr[:match.start(1)] + str(percent)
                self.display_var.set(self.current_expression)
            else:
                self.current_expression += '%'
                self.display_var.set(self.current_expression)
        except:
            self.current_expression += '%'
            self.display_var.set(self.current_expression)
    
    def append_constant(self, const):
        if const == 'π':
            value = str(math.pi)
        elif const == 'e':
            value = str(math.e)
        
        if '.' in value:
            value = value.rstrip('0').rstrip('.')
        
        self.current_expression += value
        self.display_var.set(self.current_expression)
    
    def handle_logic_operator(self, operator):
        if operator == 'NOT':
            if not self.current_expression:
                return
            self.logic_operator = operator
            self.current_expression = re.sub(r'NOT\(([^)]+)\)', r'\1', self.current_expression)
            self.current_expression = f"NOT({self.current_expression})"
        else:
            if not self.current_expression:
                return
            self.logic_operator = operator
            if self.current_expression[-1] in [' ', '&', '|', '^', '>', '<']:
                self.current_expression = self.current_expression.rstrip()
                self.current_expression = re.sub(r'(' + operator + r')\s*$', '', self.current_expression)
            self.current_expression += f" {operator} "
        
        self.display_var.set(self.current_expression)
    
    def handle_shift_operator(self, operator):
        if not self.current_expression:
            return
        self.shift_operator = operator
        if self.current_expression[-1] in [' ', '>', '<']:
            self.current_expression = self.current_expression.rstrip()
            self.current_expression = re.sub(r'(' + operator + r')\s*$', '', self.current_expression)
        self.current_expression += f" {operator} "
        self.display_var.set(self.current_expression)
    
    def append_to_expression(self, text):
        if self.mode == "programmer":
            if text in [btn.cget('text') for btn in self.disabled_buttons]:
                return
            
            if text in ['A', 'B', 'C', 'D', 'E', 'F'] and self.current_base != 16:
                return
        
        self.current_expression += str(text)
        self.display_var.set(self.current_expression)
        
        self.update_base_display()
    
    def clear_display(self):
        self.current_expression = ""
        self.display_var.set("")
        self.last_operator = None
        self.logic_operator = None
        self.shift_operator = None
        
        self.update_base_display()
    
    def backspace(self):
        if self.current_expression:
            self.current_expression = self.current_expression[:-1]
            self.display_var.set(self.current_expression)
            
            self.update_base_display()
    
    def toggle_sign(self):
        if not self.current_expression:
            self.current_expression = '-'
        elif self.current_expression.startswith('-'):
            self.current_expression = self.current_expression[1:]
        else:
            self.current_expression = '-' + self.current_expression
        self.display_var.set(self.current_expression)
        
        self.update_base_display()
    
    def calculate(self):
        try:
            if not self.current_expression:
                return
            
            result = 0
            if self.mode == "standard":
                expr = self.current_expression
                
                if '%' in expr:
                    expr = expr.replace('%', '*0.01')
                
                if '!' in expr:
                    while '!' in expr:
                        idx = expr.find('!')
                        i = idx - 1
                        while i >= 0 and (expr[i].isdigit() or expr[i] == '.' or expr[i] == ')'):
                            i -= 1
                        num_str = expr[i+1:idx]
                        if num_str:
                            try:
                                num = float(num_str) if '.' in num_str else int(num_str)
                                if num < 0 or num != int(num):
                                    raise ValueError("阶乘只能用于非负整数")
                                factorial_result = math.factorial(int(num))
                                expr = expr[:i+1] + str(factorial_result) + expr[idx+1:]
                            except:
                                raise ValueError("阶乘运算错误")
                
                if '^' in expr:
                    expr = expr.replace('^', '**')
                
                if '√' in expr:
                    while '√' in expr:
                        idx = expr.find('√')
                        if idx+1 < len(expr) and expr[idx+1] == '(':
                            paren_count = 1
                            j = idx + 2
                            while j < len(expr) and paren_count > 0:
                                if expr[j] == '(':
                                    paren_count += 1
                                elif expr[j] == ')':
                                    paren_count -= 1
                                j += 1
                            sqrt_expr = expr[idx+2:j-1]
                            try:
                                sqrt_value = math.sqrt(eval(sqrt_expr, {"__builtins__": None}, {
                                    "math": math, "pi": math.pi, "e": math.e
                                }))
                                expr = expr[:idx] + str(sqrt_value) + expr[j:]
                            except:
                                raise ValueError("平方根运算错误")
                        else:
                            j = idx + 1
                            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                                j += 1
                            num_str = expr[idx+1:j]
                            if num_str:
                                try:
                                    num = float(num_str) if '.' in num_str else int(num_str)
                                    if num < 0:
                                        raise ValueError("不能对负数开平方根")
                                    sqrt_value = math.sqrt(num)
                                    expr = expr[:idx] + str(sqrt_value) + expr[j:]
                                except:
                                    raise ValueError("平方根运算错误")
                
                trig_functions = ['sin', 'cos', 'tan']
                for trig in trig_functions:
                    if trig in expr:
                        start = 0
                        while True:
                            idx = expr.find(trig, start)
                            if idx == -1:
                                break
                            
                            if idx+len(trig) < len(expr) and expr[idx+len(trig)] == '(':
                                paren_count = 1
                                j = idx + len(trig) + 1
                                while j < len(expr) and paren_count > 0:
                                    if expr[j] == '(':
                                        paren_count += 1
                                    elif expr[j] == ')':
                                        paren_count -= 1
                                    j += 1
                                
                                inner_expr = expr[idx+len(trig)+1:j-1]
                                try:
                                    inner_value = eval(inner_expr, {"__builtins__": None}, {
                                        "math": math, "pi": math.pi, "e": math.e
                                    })
                                    
                                    if self.angle_mode == "deg":
                                        inner_value = math.radians(inner_value)
                                    
                                    if trig == 'sin':
                                        trig_value = math.sin(inner_value)
                                    elif trig == 'cos':
                                        trig_value = math.cos(inner_value)
                                    elif trig == 'tan':
                                        trig_value = math.tan(inner_value)
                                    
                                    expr = expr[:idx] + str(trig_value) + expr[j:]
                                    start = idx
                                except:
                                    raise ValueError(f"{trig}函数运算错误")
                            else:
                                start = idx + 1
                
                if 'exp' in expr:
                    start = 0
                    while True:
                        idx = expr.find('exp', start)
                        if idx == -1:
                            break
                        
                        if idx+3 < len(expr) and expr[idx+3] == '(':
                            paren_count = 1
                            j = idx + 4
                            while j < len(expr) and paren_count > 0:
                                if expr[j] == '(':
                                    paren_count += 1
                                elif expr[j] == ')':
                                    paren_count -= 1
                                j += 1
                            
                            inner_expr = expr[idx+4:j-1]
                            try:
                                inner_value = eval(inner_expr, {"__builtins__": None}, {
                                    "math": math, "pi": math.pi, "e": math.e
                                })
                                exp_value = math.exp(inner_value)
                                expr = expr[:idx] + str(exp_value) + expr[j:]
                                start = idx
                            except:
                                raise ValueError("exp函数运算错误")
                        else:
                            start = idx + 1
                
                if 'ln' in expr:
                    start = 0
                    while True:
                        idx = expr.find('ln', start)
                        if idx == -1:
                            break
                        
                        if idx+2 < len(expr) and expr[idx+2] == '(':
                            paren_count = 1
                            j = idx + 3
                            while j < len(expr) and paren_count > 0:
                                if expr[j] == '(':
                                    paren_count += 1
                                elif expr[j] == ')':
                                    paren_count -= 1
                                j += 1
                            
                            inner_expr = expr[idx+3:j-1]
                            try:
                                inner_value = eval(inner_expr, {"__builtins__": None}, {
                                    "math": math, "pi": math.pi, "e": math.e
                                })
                                if inner_value <= 0:
                                    raise ValueError("ln函数的参数必须大于0")
                                ln_value = math.log(inner_value)
                                expr = expr[:idx] + str(ln_value) + expr[j:]
                                start = idx
                            except:
                                raise ValueError("ln函数运算错误")
                        else:
                            start = idx + 1
                
                if 'log' in expr:
                    start = 0
                    while True:
                        idx = expr.find('log', start)
                        if idx == -1:
                            break
                        
                        if idx+3 < len(expr) and expr[idx+3] == '(':
                            paren_count = 1
                            j = idx + 4
                            while j < len(expr) and paren_count > 0:
                                if expr[j] == '(':
                                    paren_count += 1
                                elif expr[j] == ')':
                                    paren_count -= 1
                                j += 1
                            
                            inner_expr = expr[idx+4:j-1]
                            try:
                                inner_value = eval(inner_expr, {"__builtins__": None}, {
                                    "math": math, "pi": math.pi, "e": math.e
                                })
                                if inner_value <= 0:
                                    raise ValueError("log函数的参数必须大于0")
                                log_value = math.log10(inner_value)
                                expr = expr[:idx] + str(log_value) + expr[j:]
                                start = idx
                            except:
                                raise ValueError("log函数运算错误")
                        else:
                            start = idx + 1
                
                try:
                    result = eval(expr, {"__builtins__": None}, {
                        "math": math, "pi": math.pi, "e": math.e,
                        "sin": math.sin, "cos": math.cos, "tan": math.tan,
                        "sqrt": math.sqrt, "log10": math.log10, 
                        "log": math.log, "exp": math.exp,
                        "factorial": math.factorial
                    })
                    
                    if isinstance(result, float):
                        formatted = f"{result:.10f}"
                        if '.' in formatted:
                            formatted = formatted.rstrip('0').rstrip('.')
                        self.current_expression = formatted
                    else:
                        self.current_expression = str(result)
                    
                    self.display_var.set(self.current_expression)
                except Exception as e:
                    raise ValueError(f"计算错误: {str(e)}")
            
            else:
                expr = self.current_expression.strip()
                
                if '%' in expr:
                    expr = expr.replace('%', '%')
                
                if self.logic_operator:
                    if self.logic_operator == 'NOT':
                        match = re.search(r'NOT\(([^)]+)\)', expr)
                        if match:
                            num_str = match.group(1).strip()
                            try:
                                if '.' in num_str:
                                    num = int(float(num_str))
                                else:
                                    num = int(num_str, self.current_base)
                                result = ~num & 0xFFFFFFFF
                            except Exception as e:
                                raise ValueError("NOT运算格式错误")
                        else:
                            raise ValueError("NOT运算格式错误")
                    else:
                        pattern = re.compile(r'\s*' + re.escape(self.logic_operator) + r'\s*')
                        parts = pattern.split(expr)
                        parts = [p.strip() for p in parts if p.strip()]
                        if len(parts) == 2:
                            try:
                                num1_str = parts[0]
                                num2_str = parts[1]
                                if '.' in num1_str:
                                    num1 = int(float(num1_str))
                                else:
                                    num1 = int(num1_str, self.current_base)
                                if '.' in num2_str:
                                    num2 = int(float(num2_str))
                                else:
                                    num2 = int(num2_str, self.current_base)
                                
                                if self.logic_operator == 'AND':
                                    result = num1 & num2
                                elif self.logic_operator == 'OR':
                                    result = num1 | num2
                                elif self.logic_operator == 'XOR':
                                    result = num1 ^ num2
                                elif self.logic_operator == 'XNOR':
                                    result = ~(num1 ^ num2) & 0xFFFFFFFF
                            except Exception as e:
                                raise ValueError(f"{self.logic_operator}运算需要有效的数字")
                        else:
                            raise ValueError(f"{self.logic_operator}运算需要两个操作数")
                
                elif self.shift_operator:
                    pattern = re.compile(r'\s*' + re.escape(self.shift_operator) + r'\s*')
                    parts = pattern.split(expr)
                    parts = [p.strip() for p in parts if p.strip()]
                    if len(parts) == 2:
                        try:
                            num_str = parts[0]
                            shift_str = parts[1]
                            if '.' in num_str:
                                num = int(float(num_str))
                            else:
                                num = int(num_str, self.current_base)
                            shift = int(float(shift_str))
                            
                            if self.shift_operator == '<<':
                                result = num << shift
                            else:
                                result = num >> shift
                        except Exception as e:
                            raise ValueError(f"{self.shift_operator}运算需要有效的数字")
                    else:
                        raise ValueError(f"{self.shift_operator}运算需要两个操作数")
                
                else:
                    try:
                        if '.' in expr:
                            num = float(expr)
                            result = int(num)
                        else:
                            result = int(expr, self.current_base)
                    except Exception as e:
                        raise ValueError("无效的数字格式")
                
                self.current_expression = self.convert_base(result, self.current_base)
                self.display_var.set(self.current_expression)
                self.update_base_display()
                
        except ValueError as e:
            messagebox.showerror("计算错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"发生未知错误: {str(e)}")
    
    def convert_base(self, num, base):
        if num < 0:
            is_negative = True
            num = abs(num)
        else:
            is_negative = False
        
        if base == 2:
            result = bin(num)[2:]
        elif base == 8:
            result = oct(num)[2:]
        elif base == 10:
            result = str(num)
        elif base == 16:
            result = hex(num)[2:].upper()
        else:
            result = str(num)
        
        if is_negative:
            result = '-' + result
        
        return result
    
    def update_base_display(self):
        try:
            if not self.current_expression:
                self.bin_var.set("")
                self.oct_var.set("")
                self.dec_var.set("")
                self.hex_var.set("")
                return
            
            expr = self.current_expression.strip()
            if not expr:
                return
            
            if self.mode == "standard":
                try:
                    num = float(expr)
                    if num.is_integer():
                        num = int(num)
                except:
                    return
            else:
                try:
                    if '.' in expr:
                        num = float(expr)
                        num = int(num)
                    else:
                        num = int(expr, self.current_base)
                except:
                    return
            
            self.bin_var.set(self.convert_base(num, 2))
            self.oct_var.set(self.convert_base(num, 8))
            self.dec_var.set(self.convert_base(num, 10))
            self.hex_var.set(self.convert_base(num, 16))
            
        except:
            self.bin_var.set("")
            self.oct_var.set("")
            self.dec_var.set("")
            self.hex_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()