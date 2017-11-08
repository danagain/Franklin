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

const findDocuments = (collection, doc_count) => {
  return new Promise((resolve, reject) => {
    collection
      .find({})
      .toArray((err, docs) => {
        if (err) {
          reject(err);
        }
        Array.prototype.subarray=function(start,end){
     if(!end){ end=-1;}
    return this.slice(start, this.length+1-(end*-1));
      }
      if(docs.length > doc_count){
        docs = docs.subarray((docs.length-doc_count),-1);
      }
      resolve(docs);
      });
  });
};

module.exports = {
  insertDocuments,
  findDocuments
};
