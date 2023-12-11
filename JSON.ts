const data = {
  "name": "Nested JSON Example",
  "details": {
    "age": 25,
    "address": {
      "city": "Exampleville",
      "country": "JSONland"
    }
  },
  "extraInfo": "{\"key\":\"value\",\"nested\":{\"innerKey\":42}}"
};

function updateJSON(obj) {
  for (const key in obj) {
    if (typeof obj[key] === 'string') {
      try {
        // Attempt to parse the string as JSON
        const parsedValue = JSON.parse(obj[key]);

        // If parsing is successful, update the value
        obj[key] = parsedValue;
      } catch (error) {
        // Ignore parsing errors for non-JSON strings
      }
    } else if (typeof obj[key] === 'object') {
      // Recursively traverse nested objects
      updateJSON(obj[key]);
    }
  }
}

// Call the function to update the JSON
updateJSON(data);

console.log("Updated JSON:", data);
