#include <iostream>
#include <random>
#include <chrono>
#include <string>

int main(int argc, char* argv[]) {
    unsigned long long seed = std::chrono::steady_clock::now().time_since_epoch().count();
    if (argc > 1) {
        try {
            seed = std::stoull(argv[1]);
        } catch (...) {
            // Use fallback time-based seed if argument is not a valid number
        }
    }

    std::mt19937_64 rng(seed);

    std::uniform_int_distribution<int> distA(0, 10);
    int a = distA(rng);

    std::uniform_int_distribution<int> distB(a, 10);
    int b = distB(rng);

    std::cout << a << " " << b << "\n";

    return 0;
}