# utecoptimizer
# 🧠 UtecOptimizer

Herramienta de optimización de código estilo C-lite que aplica:

- ✔️ Constant Folding (Plegado de Constantes)
- ✔️ Code Hoisting (extracción de expresiones invariantes de bucles)
- ✔️ Reconstrucción aritmética sin espacios erróneos
- ✔️ Conservación de indentación original

> 📍 Proyecto de optimización para compiladores  
> 🎓 Universidad de Ingeniería y Tecnología (UTEC)  
> 👨‍💻 Desarrollado por JeanPROÁngeles

---

## 🚀 Instalación automática en 2 pasos

Abre una terminal en cualquier parte y ejecuta:

```bash
curl -O https://raw.githubusercontent.com/jeanPROangeles/utecoptimizer/main/install_utecoptimizer.sh
sh install_utecoptimizer.sh

<details> <summary><strong>📥 input2.txt</strong></summary>

```c
fun void main
var int a;
var int b;
var int c;
var int arr;

// Tarea 2: Constant Folding - Expresiones con constantes
a = 5 * 3 + 2;
b = 10 - 4 / 2;
c = (7 + 3) * 2 - 1;

// Tarea 3: Code Hoisting - Expresiones invariantes en loops
for(i=0;i<100;i++) {
  arr[x*y+z] += i;
}

for(j=0;j<50;j++) {
  arr[a*b] += j*2;
}

// Expresión que depende de variable de loop (NO debe hoisted)
for(k=0;k<20;k++) {
  arr[k*5] += 10;
}

// Múltiples expresiones invariantes
for(m=0;m<30;m++) {
  arr[x+y] += m;
  arr[a*2+b] += m*3;
}

// Expresión compleja invariante
for(n=0;n<40;n++) {
  arr[(x+y)*z-a] += n;
}

print(a);
print(b);
print(c);
print(arr);
endfun
```
</details>

<details> <summary><strong>⚙️ output2.txt (generado automáticamente)</strong></summary>

```c
t0 = ((x*y)+z);
t1 = (a*b);
t2 = (x+y);
t3 = ((a*2)+b);
t4 = (((x+y)*z)-a);

fun void main
var int a;
var int b;
var int c;
var int arr;

// Tarea 2: Constant Folding - Expresiones con constantes
a = 17;
b = 8;
c = 19;

// Tarea 3: Code Hoisting - Expresiones invariantes en loops
for(i=0;i<100;i++) {
  arr[t0] += i;
}

for(j=0;j<50;j++) {
  arr[t1] += j*2;
}

// Expresión que depende de variable de loop (NO debe hoisted)
for(k=0;k<20;k++) {
  arr[k*5] += 10;
}

// Múltiples expresiones invariantes
for(m=0;m<30;m++) {
  arr[t2] += m;
  arr[t3] += m*3;
}

// Expresión compleja invariante
for(n=0;n<40;n++) {
  arr[t4] += n;
}

print(a);
print(b);
print(c);
print(arr);
endfun
```
</details>
