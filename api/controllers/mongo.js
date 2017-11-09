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

const findDocuments = (collection, docCount) => {
  return new Promise((resolve, reject) => {
    collection
      .find({})
      .limit(docCount)
      .sort({$natural:-1})
      .toArray((err, docs) => {
        if (err) {
          reject(err);
        }
      resolve(docs.reverse());
      });
  });
};

module.exports = {
  insertDocuments,
  findDocuments
};
