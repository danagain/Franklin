const nodemailer = require('nodemailer');

const email = (body, callback) => {

    const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
               user: 'thehunterofcoins@gmail.com',
               pass: process.env.EMAIL_PASS
           }
       }
    );

    // Message object
    const mailOptions = {
        from: 'thehunterofcoins@gmail.com', 
        to: process.env.EMAIL_TARGET,
        subject: 'The Hunter has struck', 
        html: body
      };

    transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
            console.log('Error occurred');
            callback(error.message);
        }

        callback('Message sent successfully!');
    });

}

module.exports = {
    email
}

