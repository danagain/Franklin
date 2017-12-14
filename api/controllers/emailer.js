'use strict';

const nodemailer = require('nodemailer');

const email = body => {

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
            console.log(error.message);
            return process.exit(1);
        }

        console.log('Message sent successfully!');

        // only needed when using pooled connections
        transporter.close();
    });

}

module.exports = email;

