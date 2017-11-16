const insertDocuments = (collection, data) => {
  return new Promise((resolve, reject) => {
    collection.insertOne(data, (err, result) => {
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
      .sort({ $natural: -1 })
      .toArray((err, docs) => {
        if (err) {
          reject(err);
        }
        resolve(docs.reverse());
      });
  });
};




const updateOrderStatus = (collection, uuid) => {
  return new Promise((resolve, reject) => {
    collection.findOneAndUpdate(
      { "result.uuid": uuid },
      { $set: { cancelled: true } },
      { returnNewDocument: true },
      (err, doc) => {
        if (err) {
          reject(err);
        }
        resolve(doc);
      }
    );
  });
};

const findOrderStatus = (collection, uuid) => {
  return new Promise((resolve, reject) => {
    collection.findOne({"result.uuid": uuid}, (err, doc) => {
      if (err) {
        reject(err)
      }
      resolve(doc)
    })

  });
};

module.exports = {
  insertDocuments,
  findDocuments,
  findOrderStatus,
  updateOrderStatus
};
