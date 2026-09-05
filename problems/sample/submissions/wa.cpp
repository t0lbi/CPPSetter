#include <iostream>

int main() {
    int a, b;
    if (std::cin >> a >> b) {
        std::cout << a + b + 1 << '\n';
    }
    return 0;
}