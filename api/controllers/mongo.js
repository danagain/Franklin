// Used for inserting documents into MongoDB.
const insertDocuments = (collection, data) => {
    return new Promise((resolve, reject) => {
        collection.insert(data, (err, result) => {
          if (err) { reject(err) }
          resolve(result);
        });
    })
}

module.exports = {
    insertDocuments
};

