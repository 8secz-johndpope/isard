<template>
    <b-container fluid>
        <b-row id="register" align-h="center">
            <b-col sm="10" md="6" lg="5" xl="4">
                <img id="logo" src="@/assets/logo.svg" alt="IsardVDI logo. It's a head of an Isard" />

                <h1>IsardVDI | Registre</h1>

                <b-form method="POST" :action="register()">
                    <b-form-input
                        id="code"
                        name="code"
                        type="text"
                        required
                        placeholder="Codi de registre"
                    />

                    <b-button id="submit" type="submit" variant="warning" size="lg">Registrar-se</b-button>
                </b-form>
            </b-col>
        </b-row>
    </b-container>
</template>

<script>
export default {
  name: 'register',
  methods: {
    register () {
      let redirect = new URLSearchParams(window.location.search).get(
        'redirect'
      )
      if (redirect !== '') {
        redirect = '?redirect=' + redirect
      }
      return (
                `${window.location.protocol}//${window.location.host}/api/v2/register` +
                redirect
      )
    }
  }
}
</script>

<style>
#logo {
    width: 125px;
    margin-top: 100px;
    margin-bottom: 50px;
}

#register form {
    margin: 25px;
}

#register form input {
    margin-bottom: 18px;
}
</style>
