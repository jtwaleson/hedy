import { loginForAdmin } from "../login/login";

export function goToPage(page)
{
    if (typeof page === 'string' || page instanceof String)
    {
        if(page != "")
        {
            cy.visit(page);
        }

    }
}

export function goToHome()
{
    return goToPage('/');
}

export function goToRegisterStudent()
{
    return goToPage(Cypress.env('register_student_page'));
}

export function goToRegisterTeacher()
{
    return goToPage(Cypress.env('register_teacher_page'));
}

export function goToLogin()
{
    return goToPage(Cypress.env('login_page'));
}

export function goToRecover()
{
    return goToPage(Cypress.env('recover_page'));
}

export function goToTeachersPage()
{
    return goToPage(Cypress.env('teachers_page'));
}

export function goToHedyPage()
{
    return goToPage(Cypress.env('hedy_page'));
}

export function goToAdventurePage()
{
    return goToPage(Cypress.env('adventure_page'));
}

export function goToProfilePage()
{
    return goToPage(Cypress.env('profile_page'));
}


export function goToHedyLevel2Page()
{
    return goToPage(Cypress.env('hedy_level2_page'));
}

export function goToHedyLevel5Page()
{
    return goToPage(Cypress.env('hedy_level5_page'));
}

export function goToAdminUsersPage()
{
    loginForAdmin();
    cy.get('#users_button').click();
}

export function goToAdminAdventuresPage()
{
   return goToPage(Cypress.env('admin_adventures_page'));
}

export function goToAdminAchievementsPage()
{
   return goToPage(Cypress.env('admin_achievements_page'));
}

export function goToAdminClassesPage()
{
   return goToPage(Cypress.env('admin_classes_page'));
}

// Must be logged in and able to edit an adventure
export function goToEditAdventure()
{
    goToTeachersPage();

    // takes the first adventures and goes to its edit page
    // It does not matter which adventure we take (we choose the first one)
    cy.get('#teacher_adventures tbody > :nth-child(1) [data-cy="edit-link"]')
      .click();
}

export function goToExploreProgramsPage()
{
   return goToPage(Cypress.env('explore_programs_page'));
}

export default {goToPage}
