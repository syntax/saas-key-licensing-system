function merge(left, right) {
    let array = []
    // Break out of loop if any one of the array gets empty
    while (left.length && right.length) {
        // Pick the smaller among the smallest element of left and right sub arrays
        if (left[0] < right[0]) {
            array.push(left.shift())
        } else {
            array.push(right.shift())
        }
    }

    // Concatenating the leftover elements
    // (in case we didn't go through the entire left or right array)
    // ... acts as a spread operator
    return [ ...array, ...left, ...right ]
}

function mergeSort(array) {
  const halflength = array.length / 2

  // Base case
  if(array.length < 2){
    return array
  }

  const left = array.splice(0, halflength)
  return merge(mergeSort(left),mergeSort(array))
}


array = [4, 8, 7, 2, 11, 1, 3];
console.log(mergeSort(array));
