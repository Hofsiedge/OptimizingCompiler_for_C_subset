int const A = 10000;


int   c = -7,
    d = 3;
int k = 0;
int e = 8;
int b;
int a;
int main() {
    b = c + d;
    a = c * b + d * e;
    while(a < 0) {
        a = a + 1;
        b = b * a;
    }
    e = b * e;
    return e;
}
