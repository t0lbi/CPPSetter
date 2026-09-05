#include <iostream>

int main() {
    int a, b;
    if (std::cin >> a >> b) {
        for (int i = 0; i < b; ++i) {
            a++;
        }
        std::cout << a << std::endl;
    }
    return 0;
}