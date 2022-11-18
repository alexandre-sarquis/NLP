package lematizador;

import java.util.*;
import java.io.*;

/**
 *
 * @author Erick
 */
public class toker {
    public toker()
    {}
    public ArrayList tokenizaArquivo(String arquivo) throws FileNotFoundException, IOException
    {
        ArrayList tokens = new ArrayList();
        File file = new File(arquivo); //texto de entrada
        String conteudo;

        //faz-se a leitura do arquivo de entrada
        BufferedReader br = new BufferedReader(new FileReader(arquivo));
        StringBuilder bufSaida = new StringBuilder();

        String linha;
        while( (linha = br.readLine()) != null )
        {
            bufSaida.append(linha).append(" new-paragraph ");
        }
        br.close();
        
        char[] letras = bufSaida.toString().toCharArray();// converte conteudo do arquivo de entrada em um array de caracteres

        //letras que compoem um token
        String alfabeto_letras = "- A a À à Á á Â â Ã ã Ä ä B b C c Ç ç D d E e È è É é Ê ê Ë ë F f G g H h I i Ì ì Í í Î î Ï ï J j K k L l M m N n O o Ò ò Ó ó Ô ô Õ õ Ö ö P p Q q R r S s T t U u Ù ù Ú ú Û û Ü ü V v W w X x Y y Z z 0 1 2 3 4 5 6 7 8 9";

        //separa cada letra do alfabeto em uma posicao do array
        String[] alfabeto = alfabeto_letras.split(" ");
        
        String token = "";
        for (int i=0; i<letras.length; i++)
        {
            int achou = 0;
            String letra = ""+letras[i];
            letra = letra.trim();
            for (int j=0; j<alfabeto.length; j++) //busca cada simbolo do arquivo de entrada no alfabeto
            {
                String letra2 = alfabeto[j].trim();
                if ((letra.equals(letra2)))
                {
                    achou = 1; // se match!
                }
            }
            if (achou == 1) // adiciona letra ao token
            {
                token = token+letras[i];
            }
            else
            {
                if (!(token.equals(""))) //terminou um token, adiciona ao array
                tokens.add(token);
                
                if (!(letra.equals("")))
                {
                    tokens.add(letra); //retorna o simbolo que nao pertence ao alfabeto, tal como pontuacoes
                }
                token = "";// limpa token para inicio de novo token
            }
        }
        return tokens; //retorna o array com os tokens
    }
}
