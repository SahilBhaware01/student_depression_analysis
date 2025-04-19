
# T7 – Feature Engineering and Transformation

**Task Duration:** April 06 – April 09, 2025  
**Assigned To:** Sejal  
**Dependencies:** T5 (Data Cleaning), T6 (Outlier Detection)  
**Deliverable:** Processed dataset with engineered features (`student_depression_engineered.csv`)

---

## Objective

Feature engineering is the process of creating new features from existing ones or modifying them to better capture patterns in the data. This enhances the predictive performance of machine learning models.

---

## Techniques Used

### 1. Feature Binning
- Age_Group: Derived from `Age`  
  - Categories: Teen, Young Adult, Adult
- CGPA_Category: Derived from `CGPA`  
  - Categories: Low, Average, High

Note: `Sleep_Quality` was intended but excluded due to missing base data in `Sleep Duration`.

---

### 2. Composite Feature
- Overall_Stress:  
  Created by summing `Academic Pressure`, `Work Pressure`, and `Financial Stress`, then applying Min-Max normalization.

---

### 3. Interaction Features
- Academic_x_Satisfaction: `Academic Pressure × Study Satisfaction`
- JobSat_x_WorkPressure: `Job Satisfaction × Work Pressure`

These features capture combined effects that may influence depression levels.

---

### 4. Categorical Encoding
Applied One-Hot Encoding to the following features:
- Age_Group
- CGPA_Category
- Gender
- Degree

This enables models to handle categorical values numerically.

---

### 5. Output Summary
- Engineered dataset with 54 columns and 27,901 records
- `Sleep_Quality` and `Work_Study_Load` excluded from modeling due to NaNs
- All other engineered features successfully created and validated

Final File: `student_depression_engineered.csv`  
Ready for: Data Quality Verification (T8)

---

## Reflection

This task adds meaningful structure to raw data, aligning with project goals and ML readiness. Future tasks (T14: Feature Selection, T16: Modeling) will benefit from these transformations.
