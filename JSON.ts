type JSONObject = Record<string, any>;

const data: JSONObject = {
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

function updateJSON(obj: JSONObject): JSONObject {
  return Object.fromEntries(
    Object.entries(obj).map(([key, value]) => {
      if (typeof value === 'string') {
        try {
          return [key, JSON.parse(value)];
        } catch (error) {
          // Ignore parsing errors for non-JSON strings
        }
      } else if (typeof value === 'object' && value !== null) {
        return [key, updateJSON(value)];
      }
      return [key, value];
    })
  );
}
