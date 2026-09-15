#include "gcst/showcase.h"
#include "gcst/utils.h"

#include <boost/algorithm/string.hpp>

#include <print>
#include <string>
#include <vector>
#include <format>
#include <filesystem>

namespace fs = std::filesystem;

namespace gcst::showcase
{

void std_print()
{
    std::print("════════════════════════════════════════\n");
    std::print("C++23 std::print() Feature Showcase\n");
    std::print("════════════════════════════════════════\n\n");
    
    // 1. Basic formatted output
    std::print("1. Simple output:\n");
    std::print("   Welcome to C++23!\n\n");
    
    // 2. Floating-point precision
    std::print("2. Floating-point precision:\n");
    double pi = 3.14159265359;
    std::print("   π = {:.5f}, Full: {}\n", pi, pi);
    std::print("   Scientific: {:.2e}\n\n", pi);
    
    // 3. Number bases (decimal, hex, binary, octal)
    std::print("3. Different number bases:\n");
    int number = 255;
    std::print("   Value 255: Decimal={}, Hex={:x}, Binary={:b}, Octal={:o}\n", 
               number, number, number, number);
    std::print("   Uppercase: Hex={:X}, Binary={:B}\n\n", number, number);
    
    // 4. Width and padding
    std::print("4. Width and padding:\n");
    std::print("   Left-aligned:   |{:<15}|\n", "text");
    std::print("   Right-aligned:  |{:>15}|\n", "text");
    std::print("   Center-aligned: |{:^15}|\n", "text");
    std::print("   Zero-padded:    {:05d}\n\n", 42);
    
    // 5. Positional and named arguments
    std::print("5. Positional arguments:\n");
    std::print("   {1} {0}! (swapped order)\n\n", "World", "Hello");
    
    // 6. Boolean formatting
    std::print("6. Boolean output:\n");
    bool flag = true;
    std::print("   flag = {}, inverted = {}\n\n", flag, !flag);
    
    // 7. Collections
    std::print("7. Iterating collections:\n");
    std::vector<std::string> languages = {"C++", "Rust", "Python", "Go", "Zig"};
    std::print("   Languages: [");
    for (size_t i = 0; i < languages.size(); ++i) {
        std::print("{}", languages[i]);
        if (i < languages.size() - 1) std::print(", ");
    }
    std::print("]\n\n");
    
    // 8. Combined formatting
    std::print("8. Combined formatting example:\n");
    std::print("    Hex {:0>6x} | Decimal {:0>5d} | Float {:.2f}\n\n", 255, 42, 3.7);

    // 9. Boost.Algorithm string utilities
    std::print("9. Boost.Algorithm:\n");
    
    std::string s = "  hello, boost world!  ";
    boost::trim(s);
    std::print("   trim:       '{}'\n", s);

    boost::to_upper(s);
    std::print("   to_upper:   '{}'\n", s);

    boost::to_lower(s);
    std::print("   to_lower:   '{}'\n", s);

    std::string csv = "one,two,three,four";
    std::vector <std::string> parts;
    boost::split(parts, csv, boost::is_any_of(","));
    std::print("   split csv:  [");
    for (size_t i = 0; i < parts.size(); ++i) {
        std::print("{}", parts[i]);
        if (i < parts.size() - 1) std::print(", ");
    }
    std::print("]\n");

    std::print("   starts_with 'one': {}\n", boost::starts_with(csv, "one"));
    std::print("   contains 'three':  {}\n\n", boost::contains(csv, "three"));

    std::print("════════════════════════════════════════\n");
}

}