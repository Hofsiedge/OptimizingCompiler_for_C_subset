int const A = 3;

int main() {
    int a = 0,
        b = -3,
        c = 4,
        d = 1,
        e = a + b * c;

    a = c - A * b;
    d = b * (a + c * 4);

    while(a > 10) {
        d = d - 1;
        while (b < 10) {
            while (c > 1){
                c = c - 10;
            }
            e = e - b;
            b = b + 10 * a;
        }
        a = a - c;
    }

    d = a * b * (c + e - 3 * 5) + 4;

    return 0;
}
