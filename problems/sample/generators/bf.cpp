#include <iostream>
#include <random>
#include <chrono>
#include <cstdlib>

int main(int argc, char* argv[]) {
    unsigned int seed;
    if (argc > 1) {
        seed = static_cast<unsigned int>(std::atoi(argv[1]));
    } else {
        seed = std::chrono::steady_clock::now().time_since_epoch().count();
    }

    std::mt19937 rng(seed);
    std::uniform_int_distribution<int> dist(0, 10);

    int A = dist(rng);
    int B = dist(rng);

    std::cout << A << " " << B << "\n";

    return 0;
}