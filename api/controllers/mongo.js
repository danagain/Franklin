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

/*
I am making this function to find the last buy entry into the mongo database.
I can then use this to send the buy order uuid back to hunter from the web-api
when we need to cancel the order
*/
const getLastOrder = (collection) => {
  return new Promise((resolve, reject) => {
    collection
      .find({})
      .limit(1)
      .sort({ $natural: -1 })
      .toArray((err, docs) => { //All this array stuff is not necessary but im
        //not confident enough with javascript to try and write this myself
        //ill leave this job for you Flynn :P
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
  updateOrderStatus,
  getLastOrder
};
