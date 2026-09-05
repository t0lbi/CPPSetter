#include <iostream>

int main() {
    // Optimize input/output operations for competitive programming
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    int a, b;
    if (std::cin >> a >> b) {
        std::cout << a + b << "\n";
    }

    return 0;
}