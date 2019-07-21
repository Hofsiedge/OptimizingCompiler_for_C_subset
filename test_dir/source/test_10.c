int const A = 100;

int a = 7,
    b = -1,
    c = -3;

int const B = 1000;

int main() {

    int d = 3;
    int e = 5;
    int const C = -10;

    e = C;
    d = e;
    a = b * 7 - e * d + a;
    e = b / c;
    c = e - 1;
    while (d <= 0){
        d = d + 1;
        a = a + 3;
    }
    e = d;

    return e;
}
