# Description
Small program to explore the logistic map $f(x, a) = a \cdot x \cdot (1 - x)$.  

# Setup:  
Install requirements with  
```
pip install -r requirements.txt
```
Run with 
```
python main.py
```

# Left window: Cobweb of logistic map
x-axis: $x$  
y-axis: $f(x)$  
Green line: Iteration $x_{n+1} = f(x_n, a)$  

Initial condition $x_0$ and $a$ can be changed using keys or clicking on the bifurcation diagram.
$~$  
  
# Right window: Corrsponding Bifurcation diagram  
x-axis: $a$ - parameter  
y-axis: $x_0$ - intial condition of iteration  
Red points: Detected cycles after $n$ iterations  
White points: Limit points after $n$ iterations (Higher-order cycles or other (chaotic) attractors). By chance also some unstable attractors might be visible.

Each pixel is treated as initial condition $[x_0, a]$ and $n$ (default 10.000) iterations are carried out to study the limit behaviour and find attractors. 
The cobweb shows these iterations for 1 such initial condition.
$~$  

# Controls:  
Click window bar before applying control actions.  
Click on bifurcation diagram to set both $x_0$ and $a$ for cobweb (pink square).  

## Both
Arrow keys: Move screen  
Del/Ins: Zoom in/out  
Pos1(Home)/End: Scale horizontal axis  
Page up/down: Scale vertical axis  

## Cobweb
Numpad /,* (Divide/Multiply): Decrease/increase $a$  
Numpad 4/6: Decrease/increase $x_0$  
Numpad -/+: Decrease/increase "iterated".  
$\qquad\qquad\qquad$ E.g. by default "iterated = 1", so $x_{n+1} = f(x_n,a)$.  
$\qquad\qquad\qquad$ For "iterated = 2", $x_{n+1} = f(f(x_n,a),a)$

## Bifurcation
Numpad 1/2: Decrease/increase number of iterations  
