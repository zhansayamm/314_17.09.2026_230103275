"""
salt.py -- Task 0.2: Deterministic Student ID Salting

Each student's problem dimensions are cryptographically bound to their
8-digit Student ID, so results cannot be copied between students.
"""
import hashlib, os


def get_student_params(student_id: str):
    h = int(hashlib.sha256(student_id.encode('utf-8')).hexdigest()[:8], 16)
    # Salted matrix dimension N between 1024 and 1536 (multiple of 64)
    N = 1024 + ((h % 9) * 64)
    # Salted stride benchmark buffer size: 2^24 elements (~134 MB double-precision)
    buffer_elements = 16_777_216
    # Seed for deterministic random number generation
    seed = h % 100_007
    return {"student_id": student_id, "N": N, "buffer_elements": buffer_elements, "seed": seed}


if __name__ == "__main__":
    import json, sys
    if len(sys.argv) != 2:
        sys.exit("usage: python3 src/salt.py <8-digit-student-id>")
    print(json.dumps(get_student_params(sys.argv[1]), indent=2))