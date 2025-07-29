#!/usr/bin/env python3

def save_id_numbers(id_numbers, filename='patient_ids.txt'):
    """Save the set of ID numbers to a text file"""
    with open(filename, 'w', encoding='utf-8') as f:
        for number in sorted(id_numbers):
            f.write(f"{number}\n")

def load_id_numbers(filename='patient_ids.txt'):
    """Load ID numbers from a text file into a set"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        return set()
