// Used for inserting documents into MongoDB.
const insertDocuments = (collection, data) => {
  return new Promise((resolve, reject) => {
    collection.insert(data, (err, result) => {
      if (err) {
        reject(err);
      }
      resolve(result);
    });
  });
};
const findDocuments = (collection) => {
  return new Promise((resolve, reject) => {
    collection.find({}).toArray((err, docs) => {
      if (err) {
        reject(err);
      }
      resolve(docs);
    });
  });
};

module.exports = {
  insertDocuments,
  findDocuments
};
