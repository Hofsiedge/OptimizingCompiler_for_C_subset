int main(){
    int a = 0;
    int b = 3;
    a = b - 5;
    while (a < 10) {
        a = a + b;
        b = a;
    }
    int c = b - 1;
    return 0;
}
