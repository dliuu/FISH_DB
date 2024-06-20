This repository GETs schema-defined data from all production Bubble applications in the FISH project and hosts them in a single, unified, postgres database in PG Admin. Platform specific data is exposed by each Platform’s Bubble API endpoint.
 
IDs
Every record contains a unique_id in their respective Bubble application, and each production application will be assigned a unique_platform_number. The centralized database contains unique ids in the form unique_platform_number_unique_id.
 
Schema
Objects are relational and schema defined in the centralized database— Loan, Loan Application, Contact, Company, Funding, Payment, Disbursement. Each platform can contain custom development, and additional columns from custom development will be contained in separate objects, linked by foreign key. For example, for Platform 1, the object P1_Loan is linked to Loan by foreign key, and contains all additional data points necessary for Platform 1’s processing and servicing of loans.
 
Reoccurring Functions
 
1. [example1] Postmark.js: runs reoccurring email reminders on late payments. Runs every day.
2. [example2] de-duplicate.js: looks for duplicate records and sends alerts to the system admins. Runs every day.
3. [example3] payment_validation.js: looks for payment, funding, and disbursement records, and validates them for updated fields. Runs every 12 hours.
 
Pipeline
 
get_data.py GETs data from each bubble application on a daily, reoccurring basis.
 
validate.py validates each row of data to either INSERT/MODIFY data in the centralized database, or ignore the row if it is unchanged.
 
update.js modifies data on each respective Bubble application from the centralized database on a daily, reoccurring basis.
