# Linked Open Data Jaccard Recommendation Algorithm

## Descrição do algoritmo:
Codificação de um algoritmo de recomendação explicável baseado em conteúdo KNN 
utilizando Jaccard e Linked Open Data.

A similaridade entre itens é realizada por Jaccard entre as propriedades retornadas pela DBPedia 
(https://wiki.dbpedia.org/) e as explicações são obtidas a partir das propriedades em comum entre os itens de
perfil do usuário e o item recomendado. Por fim, o ranqueamento das propriedades é realizado a partir de um
TF-IDF adaptado para a LOD em que TF é a quantidade de vezes que a propriedade é referenciada por itens de 
perfil dividida pela quantidade de itens de perfil e o IDF é o log da divisão entre a quantidade total
de itens no dataset pela quantidade de vezes que um item possui a propriedade.

## Reprodução:

### Do projeto enviado pelo autor
- Importar dependências (ver seção Créditos de biliotecas para as utilizadas e suas versões);
- Descompactar projeto;
- Abrir projeto no PyCharm
- Rodar código

### Do git
- Importar dependências (ver seção Créditos de biliotecas para as utilizadas e suas versões);
- Baixar projeto;
- Baixar dataset (https://github.com/sisinflab/LinkedDatasets/tree/master/facebook_movies);
- Ajustar nas classes os parâmetros para geração dos arquivos auxiliares e caminhos de arquivos.

## Classes:
- JacLodRecommendationEngine: Recomendador proposto baseado em Jaccard;
- Explanations: Classe que gera as explicações;
- CosineBaseline: Algoritmo colaborativo ITEM-KNN utilizado para comparação de análise estatistica.

## Libs criadas:
- sparql_utils: funções de consulta na DBpedia;
- evaluation_utils: funções de implementação do MAP.

## Main:
O arquivo principal (main.py) foi desenvolvido para exibir os itens assistidos para 3 usuários aleatórios da base de 
dados, suas recomendações e respectivas explicações.

## Créditos de bibliotecas:
Para instalar utilizar comando: 
    
    pip install <lib>==<version>

* [numpy 1.19.1](https://numpy.org/)
* [pandas 1.0.4](https://pandas.pydata.org/)
* [scipy 1.5.0](https://www.scipy.org/)
* [SPARQLWrapper 1.8.5](https://github.com/RDFLib/sparqlwrapper)

## Consulta SPARQL
    SELECT DISTINCT *
    WHERE { 
        <movie_uri> ?prop ?obj.
        FILTER( 
            ?prop = dbo:cinematography || ?prop = dbo:director || ?prop = dbo:distributor || 
            ?prop = dbo:editing || ?prop = dbo:musicComposer || ?prop = dbo:producer || 
            ?prop = dbo:starring || ?prop = dct:subject || ?prop = foaf:name
        )   
    }

## Exemplos de retornos

### Exemplo 1:
    ----- MOVIES WATCHED BY THE USER 5729 -----
    Avatar
    Click
    National Treasure
    Mr. Brooks
    My Sister's Keeper
    Thirteen
    Eclipse
    Marley & Me
    Troy
    Austin Powers
    The Curse of the Black Pearl
    300
    Star Wars
    The Blind Side
    Anger Management
    50 First Dates
    Kingdom of Heaven
    
    ----- MOVIES RECOMMENDED TO THE USER 5729 ----- 
    The Empire Strikes Back
    The Longest Yard
    You Don't Mess with the Zohan
    National Treasure: Book of Secrets
    Mr Deeds
    
    ----- EXPLANATIONS TO THE USER 5729 -----
    Because you like american epic films such as "Avatar", "Troy", "300", "Star Wars" and "Kingdom of Heaven" watch "The Empire Strikes Back" with this same characteristic
    Because you like the editing of Jeff Gourson of "Click", "Anger Management" and "50 First Dates" watch "The Longest Yard" with this same characteristic
    Because you like the producer Jack Giarraputo of "Click", "Anger Management" and "50 First Dates" watch "You Don't Mess with the Zohan" with this same characteristic
    Because you like 2000s adventure films such as "Avatar", "National Treasure", "The Curse of the Black Pearl" and "300" watch "National Treasure: Book of Secrets" with this same characteristic
    Because you like the producer Jack Giarraputo of "Click", "Anger Management" and "50 First Dates" watch "Mr Deeds" with this same characteristic

### Exemplo 2:
    ----- MOVIES WATCHED BY THE USER 6364 -----
    WALL-E
    Spider-Man
    Rambo
    The Thing
    The Incredible Hulk
    Underworld: Rise of the Lycans
    Pirates of the Caribbean
    Rocky
    Blade
    Aliens
    Blade II
    Maverick
    ----- MOVIES RECOMMENDED TO THE USER 6364 -----
    Spider-Man 2
    Rocky II
    Blade: Trinity
    Spider-Man 3
    Rocky III
    ----- EXPLANATIONS TO THE USER 6364 -----
    Because you like american action films such as "Spider-Man", "The Incredible Hulk", "Blade" and "Blade II" watch "Spider-Man 2" with this same characteristic
    Because you like 1970s sports films such as "Rocky" watch "Rocky II" with this same characteristic
    Because you like american action films such as "Spider-Man", "The Incredible Hulk", "Blade" and "Blade II" watch "Blade: Trinity" with this same characteristic
    Because you like american action films such as "Spider-Man", "The Incredible Hulk", "Blade" and "Blade II" watch "Spider-Man 3" with this same characteristic
    Because you like films starring Burgess Meredith like "Rocky" watch "Rocky III" with this same characteristic
    
### Exemplo 3:

    ----- MOVIES WATCHED BY THE USER 6087 -----
    The Devil Wears Prada
    Spirited Away
    Moulin Rouge
    Rent
    The Proposal
    The Phantom of the Opera
    He's Just Not That Into You
    The Demon Barber of Fleet Street
    Chicago
    Aladdin
    Friday the 13th
    The Princess Diaries
    Killers
    ----- MOVIES RECOMMENDED TO THE USER 6087 -----
    The Princess Diaries 2: Royal Engagement
    Maid in Manhattan
    Coyote Ugly
    Raising Helen
    License to Wed
    ----- EXPLANATIONS TO THE USER 6087 -----
    Because you like films starring Héctor Elizondo like "The Princess Diaries" watch "The Princess Diaries 2: Royal Engagement" with this same characteristic
    Because you like the cinematography of Karl Walter Lindenlaub of "The Princess Diaries" watch "Maid in Manhattan" with this same characteristic
    Because you like 2000s musical films such as "Rent", "The Phantom of the Opera", "The Demon Barber of Fleet Street" and "Chicago" watch "Coyote Ugly" with this same characteristic
    Because you like films directed by Garry Marshall such as "The Princess Diaries" watch "Raising Helen" with this same characteristic
    Because you like films directed by Ken Kwapis such as "He's Just Not That Into You" and the director Ken Kwapis of "He's Just Not That Into You" watch "License to Wed" with these same characteristics
    
### Exemplo 4:

    ----- MOVIES WATCHED BY THE USER 6401 -----
    Forrest Gump
    Saving Private Ryan
    American Pie
    Eat Pray Love
    Meet the Fockers
    Paul
    Home Alone
    A Beautiful Mind
    Terms of Endearment
    The Smurfs
    Whatever Works
    ----- MOVIES RECOMMENDED TO THE USER 6401 -----
    Home Alone 2: Lost in New York
    Meet the Parents
    American Pie 2
    Little Fockers
    Ordinary People
    ----- EXPLANATIONS TO THE USER 6401 -----
    Because you like Home Alone (franchise) such as "Home Alone" watch "Home Alone 2: Lost in New York" with this same characteristic
    Because you like films starring Teri Polo like "Meet the Fockers" watch "Meet the Parents" with this same characteristic
    Because you like the music composer David Nessim Lawrence of "American Pie" and films starring Thomas Ian Nicholas like "American Pie" watch "American Pie 2" with these same characteristics
    Because you like films directed by Paul Weitz such as "American Pie" watch "Little Fockers" with this same characteristic
    Because you like best Drama Picture Golden Globe winners such as "Forrest Gump", "Saving Private Ryan", "A Beautiful Mind" and "Terms of Endearment" watch "Ordinary People" with this same characteristic