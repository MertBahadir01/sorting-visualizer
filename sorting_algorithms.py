"""
sorting_algorithms.py
Each algorithm is a generator yielding:
    (array_snapshot, compared_indices, swapped_indices, sorted_indices)
"""


def bubble_sort(arr):
    arr = arr[:]
    n = len(arr)
    sorted_indices = set()
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            yield arr[:], [j, j + 1], [], sorted_indices
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
                yield arr[:], [], [j, j + 1], sorted_indices
        sorted_indices.add(n - i - 1)
        if not swapped:
            for k in range(n - i - 1):
                sorted_indices.add(k)
            break
    sorted_indices = set(range(n))
    yield arr[:], [], [], sorted_indices


def selection_sort(arr):
    arr = arr[:]
    n = len(arr)
    sorted_indices = set()
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            yield arr[:], [min_idx, j], [], sorted_indices
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            yield arr[:], [], [i, min_idx], sorted_indices
        sorted_indices.add(i)
    sorted_indices = set(range(n))
    yield arr[:], [], [], sorted_indices


def insertion_sort(arr):
    arr = arr[:]
    n = len(arr)
    sorted_indices = {0}
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        yield arr[:], [i, max(j, 0)], [], sorted_indices
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            yield arr[:], [], [j, j + 1], sorted_indices
            j -= 1
        arr[j + 1] = key
        sorted_indices.add(i)
        yield arr[:], [], [j + 1], sorted_indices
    sorted_indices = set(range(n))
    yield arr[:], [], [], sorted_indices


def merge_sort(arr):
    arr = arr[:]
    n = len(arr)
    sorted_indices = set()

    def _merge(a, left, right):
        if right - left <= 1:
            return
        mid = (left + right) // 2
        yield from _merge(a, left, mid)
        yield from _merge(a, mid, right)
        left_part = a[left:mid]
        right_part = a[mid:right]
        i = j = 0
        k = left
        while i < len(left_part) and j < len(right_part):
            yield a[:], [left + i, mid + j], [], sorted_indices
            if left_part[i] <= right_part[j]:
                a[k] = left_part[i]; i += 1
            else:
                a[k] = right_part[j]; j += 1
            yield a[:], [], [k], sorted_indices
            k += 1
        while i < len(left_part):
            a[k] = left_part[i]
            yield a[:], [], [k], sorted_indices
            i += 1; k += 1
        while j < len(right_part):
            a[k] = right_part[j]
            yield a[:], [], [k], sorted_indices
            j += 1; k += 1
        for idx in range(left, right):
            sorted_indices.add(idx)

    yield from _merge(arr, 0, n)
    sorted_indices = set(range(n))
    yield arr[:], [], [], sorted_indices


def quick_sort(arr):
    arr = arr[:]
    n = len(arr)
    sorted_indices = set()

    def _quick(a, low, high):
        if low < high:
            pivot_val = a[high]
            i = low - 1
            for j in range(low, high):
                yield a[:], [j, high], [], sorted_indices
                if a[j] <= pivot_val:
                    i += 1
                    a[i], a[j] = a[j], a[i]
                    yield a[:], [], [i, j], sorted_indices
            a[i + 1], a[high] = a[high], a[i + 1]
            pivot = i + 1
            sorted_indices.add(pivot)
            yield a[:], [], [pivot, high], sorted_indices
            yield from _quick(a, low, pivot - 1)
            yield from _quick(a, pivot + 1, high)

    yield from _quick(arr, 0, n - 1)
    sorted_indices = set(range(n))
    yield arr[:], [], [], sorted_indices


def heap_sort(arr):
    arr = arr[:]
    n = len(arr)
    sorted_indices = set()

    def heapify(a, size, root):
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2
        if left < size:
            yield a[:], [largest, left], [], sorted_indices
            if a[left] > a[largest]:
                largest = left
        if right < size:
            yield a[:], [largest, right], [], sorted_indices
            if a[right] > a[largest]:
                largest = right
        if largest != root:
            a[root], a[largest] = a[largest], a[root]
            yield a[:], [], [root, largest], sorted_indices
            yield from heapify(a, size, largest)

    for i in range(n // 2 - 1, -1, -1):
        yield from heapify(arr, n, i)

    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        sorted_indices.add(i)
        yield arr[:], [], [0, i], sorted_indices
        yield from heapify(arr, i, 0)

    sorted_indices = set(range(n))
    yield arr[:], [], [], sorted_indices


def shell_sort(arr):
    arr = arr[:]
    n = len(arr)
    sorted_indices = set()
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            yield arr[:], [j, max(j - gap, 0)], [], sorted_indices
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                yield arr[:], [], [j, j - gap], sorted_indices
                j -= gap
            arr[j] = temp
        gap //= 2
    sorted_indices = set(range(n))
    yield arr[:], [], [], sorted_indices


ALGORITHMS = {
    "Bubble Sort":    bubble_sort,
    "Selection Sort": selection_sort,
    "Insertion Sort": insertion_sort,
    "Merge Sort":     merge_sort,
    "Quick Sort":     quick_sort,
    "Heap Sort":      heap_sort,
    "Shell Sort":     shell_sort,
}

ALGO_INFO = {
    "Bubble Sort":    "O(n²) avg  ·  O(n) best  ·  Stable",
    "Selection Sort": "O(n²) avg  ·  O(n²) best  ·  Unstable",
    "Insertion Sort": "O(n²) avg  ·  O(n) best  ·  Stable",
    "Merge Sort":     "O(n log n) avg  ·  Stable",
    "Quick Sort":     "O(n log n) avg  ·  O(n²) worst  ·  Unstable",
    "Heap Sort":      "O(n log n) avg  ·  Unstable",
    "Shell Sort":     "O(n log²n) avg  ·  Unstable",
}
